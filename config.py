FORBIDDEN_COMMANDS = [
    '/etc/shadow',
    '/etc/gshadow',
    '/etc/passwd',
    '/etc/sudoers',
    '/etc/ssh',
    '/root/.ssh',

    'rm',
    'rm -rf',
    'unlink',
    'shred',
    'wipefs',
    'dd',
    'mkfs',

    'chmod',
    'chmod 777',
    'chown',
    'setfacl',

    'useradd',
    'userdel',
    'usermod',
    'passwd',
    'sudo -i',
    'sudo su',

    'ssh-keygen',
    'ssh-copy-id',
    'sshd',

    'systemctl stop',
    'systemctl disable',
    'kill -9',

    'journalctl --vacuum',
    'truncate',
]


IGNORE_COMM = {
    'systemd',
    'gnome-shell',
    'dbus-daemon',
    'pipewire',
    'pulseaudio',
    'vte-spawn',
}

ENABLE_ROOT_NOTIFICATION = True
ENABLE_USER_WARNING = True
ENABLE_SCREEN_LOCK = True
ENABLE_LOGOUT = False
ENABLE_ACCOUNT_LOCK = True
ENABLE_AUTO_UNLOCK = True 
ACCOUNT_LOCK_DURATION = 900
ACCOUNT_LOCK_THRESHOLD = 5 
VIOLATION_THRESHOLD = 2
