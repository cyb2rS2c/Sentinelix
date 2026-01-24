# RedFlag

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/%7C%20Linux-green?logo=linux)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-1.0-orange)

---

> **RedFlag** is a real-time user activity monitoring service for Linux systems. It tracks attempts to run forbidden or sensitive commands and immediately alerts both administrators and users. All violations are logged for accountability, and the service can take automated actions such as sending warnings, locking screens, temporarily locking user accounts, or logging users out. 

---

## Features

- Monitors commands in real-time using `journalctl`.
- Detects **forbidden commands** (customizable via `config.py`).
- Sends warnings directly to the user's terminal.
- Logs violations to:
  - `/var/log/user_activity.log` (central log for admins)
  - `/var/log/user_warnings/<username>.log` (per-user warnings)
- Notifies root via `wall` for critical violations.
- Supports configurable actions as mentioned here: [Configuration](https://github.com/cyb2rS2c/RedFlag/blob/main/README.md#configuration)

---

## Installation

1. Clone the repository:

```bash
sudo su;sudo git clone https://github.com/cyb2rS2c/RedFlag.git /opt/RedFlag
cd /opt/RedFlag;chmod +x fix_owner.sh;./fix_owner.sh
```

## Configuration

All configuration is handled in **config.py**:

- FORBIDDEN_COMMANDS: Commands that trigger warnings or enforcement actions.
- IGNORE_COMM: Processes to skip monitoring.
- ENABLE_ROOT_NOTIFICATION: Alert root using wall.
- ENABLE_USER_WARNING: Show warnings in user terminals and log to per-user files.

- ENABLE_SCREEN_LOCK: Lock active user sessions on violation.
- ENABLE_LOGOUT: Terminate active user sessions after repeated violations.
- ENABLE_ACCOUNT_LOCK: Lock the user account to prevent future logins.
- ENABLE_AUTO_UNLOCK: Automatically unlock the account after a timeout.

- VIOLATION_THRESHOLD: Number of violations before logout.
- ACCOUNT_LOCK_THRESHOLD: Number of violations before account lock.
- ACCOUNT_LOCK_DURATION: Duration (in seconds) before an auto-unlocked account is restored.


## Example configuration
```
ENABLE_ROOT_NOTIFICATION = True
ENABLE_USER_WARNING = True

# Enforcement actions
ENABLE_SCREEN_LOCK = True          # Lock active sessions on violation
ENABLE_LOGOUT = False              # Terminate sessions after threshold
ENABLE_ACCOUNT_LOCK = True         # Lock user account (disable logins)
ENABLE_AUTO_UNLOCK = True          # Automatically unlock after timeout

# Thresholds
VIOLATION_THRESHOLD = 2            # Violations before logout
ACCOUNT_LOCK_THRESHOLD = 5         # Violations before account lock

# Timers
ACCOUNT_LOCK_DURATION = 900        # Seconds (15 minutes)
```

2. Deploy the service:
```bash
./deploy.sh
```

## Usage

Once deployed, RedFlag runs in the background as a systemd service.

To check its status:
```bash
sudo systemctl status user-monitor.service
```
To view logs:
- Admin log:
```bash
sudo cat /var/log/user_activity.log
```
- User-specific warnings:
```bash
sudo cat /var/log/user_warnings/<username>.log
```
## Notes
- If an account has been locked by RedFlag and you don’t want to wait for the 15‑minute auto‑unlock period, you can manually unlock it with:
```bash
sudo usermod -U <username>
```

## Author
cyb2rS2c - [GitHub Profile](https://github.com/cyb2rS2c)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer!

This code is provided "as-is" without any warranty. The author is not responsible for any misuse or damage caused by the use of this software. Always practice responsible security testing.
