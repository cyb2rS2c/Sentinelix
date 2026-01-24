#!/usr/bin/env python3
import json
import subprocess
import pwd
import logging
import re
import os
from collections import defaultdict
from config import (
    FORBIDDEN_COMMANDS,
    IGNORE_COMM,
    ENABLE_ROOT_NOTIFICATION,
    ENABLE_USER_WARNING,
    ENABLE_SCREEN_LOCK,
    ENABLE_LOGOUT,
    VIOLATION_THRESHOLD,
)

violations = defaultdict(int)

def setup_logger(log_file="/var/log/user_activity.log"):
    logger = logging.getLogger("UserMonitor")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s | UID: %(uid)s | COMM: %(comm)s | CMD: %(cmd)s | MSG: %(user_msg)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

def get_combined_text(entry):
    text_parts = []
    for key in ['_CMDLINE', 'COMMAND']:
        if key in entry and entry[key]:
            text_parts.append(entry[key])
    return " ".join(text_parts)

def contains_forbidden(entry):
    text = get_combined_text(entry)
    if not text:
        return False, ""
    tokens = text.replace('"', '').split()
    if tokens and tokens[0] == 'sudo':
        tokens = tokens[1:]
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden.startswith("/"):
            if forbidden in text:
                return True, text
        else:
            pattern = r'\b' + re.escape(forbidden) + r'\b'
            if re.search(pattern, text):
                return True, text
    return False, ""

def notify_root(message):
    if ENABLE_ROOT_NOTIFICATION and os.geteuid() == 0:
        subprocess.run(['wall', '-n', f'[SECURITY ALERT] {message}'], check=False)

def log_user_warning(username, message):
    log_dir = "/var/log/user_warnings"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{username}.log")
    try:
        with open(log_path, "a") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"[!] Could not log warning for {username}: {e}")

def warn_user(uid, message=None, entry=None):
    if not ENABLE_USER_WARNING:
        return
    try:
        username = pwd.getpwuid(int(uid)).pw_name
    except KeyError:
        username = f"UID {uid}"

    if message is None:
        message = f'[WARNING] Forbidden activity detected for user {username}.'

    tty = None
    if entry and 'MESSAGE' in entry:
        msg = entry['MESSAGE']
        m = re.search(r'TTY=(\S+)', msg)
        if m:
            tty = m.group(1)
    if not tty:
        try:
            who_output = subprocess.check_output(["who"], text=True)
            for line in who_output.splitlines():
                parts = line.split()
                if parts[0] == username:
                    tty = parts[1]
                    break
        except Exception:
            pass
    if tty:
        tty_path = f"/dev/{tty}"
        try:
            with open(tty_path, "w") as f:
                f.write("\n" + message + "\n\n")
        except PermissionError:
            print(f"[!] Permission denied writing to {tty_path}, run monitor as root.")
        except Exception as e:
            print(f"[!] Failed to write to {tty_path}: {e}")
    else:
        print(f"[!] Could not find TTY for {username}, cannot show warning on-screen.")

    log_user_warning(username, message)


def log_violation(uid, comm, cmd, msg):
    msg_clean = (msg[:100] + '...') if len(msg) > 100 else msg
    cmd_clean = (cmd[:50] + '...') if len(cmd) > 50 else cmd
    logger.info(
        f"{cmd_clean}",
        extra={"uid": uid, "comm": comm, "cmd": cmd_clean, "user_msg": msg_clean}
    )

last_violation = defaultdict(set)
def get_user_sessions(uid):
    """Return all active session IDs for a given UID."""
    sessions = []
    try:
        output = subprocess.check_output(
            ["loginctl", "list-sessions", "--no-legend"], text=True
        )
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2 and int(parts[1]) == int(uid):
                sessions.append(parts[0])
    except Exception as e:
        print(f"[!] Could not list sessions for UID {uid}: {e}")
    return sessions

def lock_screen(uid):
    """Lock all active sessions for a given UID."""
    if not ENABLE_SCREEN_LOCK:
        return
    sessions = get_user_sessions(uid)
    if not sessions:
        print(f"[!] No active sessions found for UID {uid}, cannot lock screen")
        return
    for session in sessions:
        subprocess.run(["loginctl", "lock-session", session], check=False)
        print(f"[+] Locked session {session} for UID {uid}")

def logout_user(uid):
    """Logout all active sessions for a given UID."""
    if not ENABLE_LOGOUT:
        return
    sessions = get_user_sessions(uid)
    for session in sessions:
        subprocess.run(["loginctl", "terminate-session", session], check=False)
        print(f"[+] Terminated session {session} for UID {uid}")

def handle_violation(uid, cmd, comm="unknown", msg="", entry=None):
    """Handle forbidden command violations."""
    if cmd in last_violation[uid]:
        return
    last_violation[uid].add(cmd)
    violations[uid] += 1
    print(f"[!] UID {uid} violated: {cmd}")
    log_violation(uid, comm, cmd, msg)
    notify_root(f"UID {uid} executed forbidden command: {cmd}")

    if ENABLE_USER_WARNING:
        warn_user(uid, f"[WARNING] You executed a forbidden command: {cmd}", entry=entry)

    if ENABLE_SCREEN_LOCK:
        lock_screen(uid)

    if ENABLE_LOGOUT and violations[uid] >= VIOLATION_THRESHOLD:
        logout_user(uid)

def monitor_journal():
    process = subprocess.Popen(
        ["journalctl", "-f", "-o", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    try:
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            comm = entry.get('_COMM', '')
            if comm in IGNORE_COMM:
                continue
            uid = entry.get('_SYSTEMD_OWNER_UID') or entry.get('_UID')
            try:
                uid_int = int(uid)
            except (ValueError, TypeError):
                continue
            if uid_int == 0:
                continue
            forbidden, match_text = contains_forbidden(entry)
            if forbidden:
                handle_violation(uid, match_text, comm=comm, msg=entry.get('MESSAGE', ''), entry=entry)
    except KeyboardInterrupt:
        print("\n[!] Monitor stopped by user")
    finally:
        process.terminate()
        process.wait()
        print("[+] journalctl process terminated cleanly")

if __name__ == "__main__":
    try:
        print("[+] Real-time User Activity Monitor started")
        monitor_journal()
    except KeyboardInterrupt:
        print("\n[!] Monitor stopped by user")
