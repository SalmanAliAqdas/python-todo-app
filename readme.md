# Python To-Do List App

A command-line to-do list written in Python with priorities, due dates, search and statistics. Your tasks are saved automatically in a file, so they are still there the next time you open the app.

## Features
- Add, list, edit and delete tasks
- Mark tasks as done or not done
- **Priorities**: high, normal, low
- **Due dates**: `@today`, `@tomorrow` or `@YYYY-MM-DD`, with automatic OVERDUE warnings
- Filter the list: all, pending, done, overdue, today, high
- Search tasks by word
- Statistics summary with completion percentage
- Clear all finished tasks (asks for confirmation first)
- Tasks saved automatically in `tasks.json`
- Files saved by version 1 still load correctly
- Safe handling of mistakes (wrong id, bad date, empty text, unknown command)
- Backup copy kept if the save file is ever damaged
- Automated tests (26)

## Requirements
- Python 3 installed
- A terminal (for example the one inside VS Code)

No extra packages are needed.

## How to run
```
python todo.py
```
If `python` is not recognized on Windows, use `py todo.py`.

## Commands
| Command | What it does |
|---|---|
| `add Buy milk` | add a task |
| `add Pay bill !high @2026-10-20` | add with priority and due date |
| `add Call Ali !low @tomorrow` | priority and date can go anywhere in the line |
| `list` | show all tasks |
| `list pending` / `list done` | unfinished / finished tasks |
| `list overdue` | unfinished tasks past their due date |
| `list today` | unfinished tasks due today |
| `list high` | unfinished high-priority tasks |
| `search milk` | find tasks containing a word |
| `stats` | show a summary |
| `done 1` / `undone 1` | mark task 1 done / not done |
| `edit 1 Buy bread` | change the text of task 1 |
| `priority 1 high` | set priority (high, normal, low) |
| `due 1 tomorrow` | set due date (`due 1 none` removes it) |
| `delete 1` | delete task 1 |
| `clear` | delete all finished tasks (asks first) |
| `help` | show the commands |
| `q` | quit |

## Example session
```
To-Do List v2  (type 'help' for commands, 'q' to quit)
You have 0 unfinished task(s), 0 overdue.
> add Pay electricity bill !high @tomorrow
> add Buy milk
> list
  1. [ ] Pay electricity bill  !high  (due 2026-10-16)
  2. [ ] Buy milk
(0 of 2 done)
> done 2
> stats
Total: 2   Done: 1 (50%)   Pending: 1
Overdue: 0   High priority pending: 1
> q
Goodbye!
```

## Where are my tasks saved?
In `tasks.json`, in the same folder as `todo.py`. It is listed in `.gitignore`, so your personal tasks are not uploaded to GitHub.

## Running the tests
```
python -m unittest -v
```

## Project structure
- `todo.py`: the app
- `test_todo.py`: automated tests
- `.gitignore`: files Git should ignore
- `readme.md`: this file

## Version history
- **v2**: priorities, due dates, overdue warnings, search, stats, more filters
- **v1**: add, list, edit, delete, done/undone, clear, automatic saving

## Possible future improvements
- Recurring tasks
- Categories or tags
- A simple web or graphical version
