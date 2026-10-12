# Python To-Do List App

A command-line to-do list written in Python. Your tasks are saved automatically in a file, so they are still there the next time you open the app.

## Features
- Add, list, edit and delete tasks
- Mark tasks as done or not done
- Filter the list: all, pending or done
- Clear all finished tasks (asks for confirmation first)
- Tasks saved automatically in `tasks.json`
- Safe handling of mistakes (wrong id, empty text, unknown command)
- Protects against a damaged save file by keeping a backup copy
- Automated tests

## Requirements
- Python 3 installed
- A terminal (for example the one inside VS Code)

No extra packages are needed.

## How to run
```
python todo.py
```
If `python` is not recognized on Windows, use `py todo.py`.

## How to use it
Type a command at the `>` prompt and press Enter.

| Command | What it does |
|---|---|
| `add Buy milk` | add a task |
| `list` | show all tasks |
| `list pending` | show unfinished tasks |
| `list done` | show finished tasks |
| `done 1` | mark task 1 as done |
| `undone 1` | mark task 1 as not done |
| `edit 1 Buy bread` | change the text of task 1 |
| `delete 1` | delete task 1 |
| `clear` | delete all finished tasks (asks first) |
| `help` | show the commands |
| `q` | quit |

## Example session
```
To-Do List  (type 'help' for commands, 'q' to quit)
You have 0 unfinished task(s).
> add Buy milk
Added task 1: Buy milk
> add Call the plumber
Added task 2: Call the plumber
> done 1
Task 1 marked done: Buy milk
> list
  1. [x] Buy milk
  2. [ ] Call the plumber
(1 of 2 done)
> clear
Delete 1 finished task(s)? (y/n): y
Deleted 1 finished task(s).
> q
Goodbye!
```

## Where are my tasks saved?
In `tasks.json`, in the same folder as `todo.py`. The file is created the first time you add a task. It is listed in `.gitignore`, so your personal tasks are not uploaded to GitHub.

## Running the tests
```
python -m unittest -v
```

## Project structure
- `todo.py`: the app
- `test_todo.py`: automated tests
- `.gitignore`: files Git should ignore
- `readme.md`: this file

## Possible future improvements
- Due dates and priorities
- Search
- A simple web or graphical version
