# SCNDERSE — Version Control System


*This is an academic project developed to apply concepts from an Operating Systems course. It is not intended for production use.*

SCNDERSE is a version control system built from scratch in Python. It models a simplified Git-like workflow where multiple users can manage local repositories, exchange files, and track changes over time — all without external dependencies. The project ships with both a desktop GUI built in Tkinter and an interactive command-line interface.

---

## How it works

Each user owns a repository folder divided into two areas: `temporal/` (staging) and `permanente/` (committed state). Files sit in staging until the user runs a commit, which moves them into the permanent area and creates a timestamped backup. When collaborating, users run update to pull files that others have committed into their own staging area before they can commit.

```
User A writes files → temporal/
        ↓
    commit
        ↓
permanente/  ←──── backup_YYYYMMDDHHMMSS/ created automatically
        ↓
    User B runs update
        ↓
User B's temporal/ ← files from A's permanente/
        ↓
    User B commits
```

The system enforces this order. If another user has committed changes you don't have yet, your commit will be blocked until you run update first. Integrity is verified by comparing SHA-256 hashes of files across repositories.

---

## Permission model

Every user can grant other users access to their repository. There are two levels:

| Permission | See permanent files | Stage / commit changes |
|---|---|---|
| `lectura` (read) | ✅ Yes | ❌ No |
| `escritura` (write) | ✅ Yes | ✅ Yes |
| Owner | ✅ Always | ✅ Always |

Permissions are stored in `data/usuarios.json`. When a permission is assigned, the system automatically replicates the full permission graph across all related repositories so no user ends up with inconsistent access.

---

## Commit

1. Verifies the user has write permission on the target repository
2. Compares SHA-256 hashes against all accessible repositories to detect divergence
3. Blocks the commit and prompts for update if any remote file differs
4. Creates a snapshot in `versions/backup_YYYYMMDDHHMMSS/` from the current `permanente/`
5. Copies everything from `temporal/` into `permanente/`
6. Clears `temporal/`

## Update

1. Scans repositories of all users who have granted access to the current user
2. Identifies files present in their `permanente/` that are missing locally
3. Copies those files into the current user's repository:
   - Into `temporal/` if the user has write permission (so they can review before committing)
   - Into `permanente/` directly if they only have read permission

---

## CLI commands

The interactive CLI launches with `python main.py` and accepts the following commands:

```
repo --user <n> --path <path>                   Create a repository at the given path
user --admin <admin> --new <n>                  Create a new user through an administrator
ls --user <user> --owner <owner>                List files in another user's repository
commit --user <n>                               Commit staged files to permanent storage
update --user <user> --owner <owner>            Pull new files from another user's repository
perm --user <user> --set <other:read/write>     Assign permissions to another user
help                                            Show available commands
exit                                            Quit
```

---

## GUI

The desktop interface is built with Tkinter. The left sidebar shows the active user, their repository list, and controls for creating users and assigning permissions. The main panel displays two file trees side by side — `temporal/` on the left and `permanente/` on the right — which update after every operation.

From the GUI you can:

- Create and switch between users
- Create repositories by selecting a folder from disk
- Create files and folders inside `temporal/`
- Rename files with a double-click
- Delete files from `permanente/`
- Run commit and update with a single button
- Browse the full backup history and restore individual files or entire snapshots

---

## Project structure

```
scnderse/
├── main.py              # CLI entry point
├── gui.py               # Desktop GUI (Tkinter)
├── interfaz.py          # Interactive command-line interface
├── usuarios.py          # User management, permissions, JSON persistence
├── repositorio.py       # Repository creation and initialization
├── version_control.py   # Commit, update, backup, and hash logic
└── data/
    └── usuarios.json    # Users and permissions database
```

Each repository on disk follows this layout:

```
<base_path>/
├── temporal/                        ← staging area
├── permanente/                      ← committed state
└── versions/
    └── backup_YYYYMMDDHHMMSS/       ← automatic snapshot per commit
```

---

## Installation

No third-party packages required. Tkinter ships with most Python distributions.

```bash
git clone <repository-url>
cd scnderse

# Launch the GUI
python gui.py

# Or use the CLI
python main.py
```

Requires Python 3.8 or higher.

---

## Known limitations

- Conflict resolution is not implemented — if two users modify the same file, the last update wins
- The permission replication logic assumes all users share the same base directory
- There is no authentication; user identity is selected from a dropdown
- The CLI `update` command requires specifying the owner explicitly; the GUI resolves this automatically

---
