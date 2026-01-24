# RedFlag

**RedFlag** is a real-time user activity monitoring service designed to track forbidden commands on Linux systems. It alerts both administrators and users when sensitive or dangerous operations are attempted, logs all violations, and can take automated actions such as warnings, screen locks, or user logouts.  

---

## Features

- Monitors commands in real-time using `journalctl`.
- Detects **forbidden commands** (customizable via `config.py`).
- Sends warnings directly to the user's terminal.
- Logs violations to:
  - `/var/log/user_activity.log` (central log for admins)
  - `/var/log/user_warnings/<username>.log` (per-user warnings)
- Notifies root via `wall` for critical violations.
- Supports configurable actions:
  - Lock user screen
  - Force logout
  - Set violation thresholds

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/cyb2rS2c/RedFlag.git
cd RedFlag
```
2. Deploy the service:
```bash
chmod +x deploy.sh;./deploy.sh
```
## Configuration (Editable)

All configuration is handled in **config.py**:
- FORBIDDEN_COMMANDS: Commands that trigger warnings or actions.
- IGNORE_COMM: Processes to skip monitoring.
- ENABLE_ROOT_NOTIFICATION: Alerts root with wall.
- ENABLE_USER_WARNING: Shows warnings in user terminals and logs to per-user files.
- ENABLE_SCREEN_LOCK / ENABLE_LOGOUT: Optional automated actions.
- VIOLATION_THRESHOLD: Number of violations before logout.

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

## Author
cyb2rS2c - [GitHub Profile](https://github.com/cyb2rS2c)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer!

This code is provided "as-is" without any warranty. The author is not responsible for any misuse or damage caused by the use of this software. Always practice responsible security testing.
