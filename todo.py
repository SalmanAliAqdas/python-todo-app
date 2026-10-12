"""Command-line to-do list app.

Tasks are saved in a file called tasks.json next to this script,
so they are still there the next time you run it.
Type 'help' to see all commands.
"""

import json
import os
from datetime import date

DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

HELP_TEXT = """\
Commands:
  add <text>          add a task            e.g.  add Buy milk
  list                show all tasks
  list pending        show only unfinished tasks
  list done           show only finished tasks
  done <id>           mark a task as done   e.g.  done 2
  undone <id>         mark a task as not done
  edit <id> <text>    change a task's text  e.g.  edit 2 Buy bread
  delete <id>         delete a task
  clear               delete all finished tasks (asks first)
  help                show this message
  q                   quit"""


# ---------- Saving and loading ----------

def load_tasks(path=DEFAULT_FILE):
    """Read tasks from disk. Returns an empty list if there is no file yet."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("unexpected file format")
        return data
    except (json.JSONDecodeError, ValueError):
        # Keep the damaged file as a backup instead of overwriting it.
        backup = path + ".broken"
        os.replace(path, backup)
        print(f"Warning: {os.path.basename(path)} was damaged. Saved a copy as {os.path.basename(backup)} and started fresh.")
        return []


def save_tasks(tasks, path=DEFAULT_FILE):
    """Write tasks to disk safely (write a temp file, then swap it in)."""
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2, ensure_ascii=False)
    os.replace(temp_path, path)


# ---------- Task operations ----------

def clean_text(text):
    text = text.strip()
    if not text:
        raise ValueError("Task text cannot be empty.")
    return text


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise ValueError(f"No task with id {task_id}.")


def add_task(tasks, text):
    text = clean_text(text)
    new_id = max((task["id"] for task in tasks), default=0) + 1
    task = {"id": new_id, "text": text, "done": False, "created": date.today().isoformat()}
    tasks.append(task)
    return task


def set_done(tasks, task_id, done=True):
    task = find_task(tasks, task_id)
    task["done"] = done
    return task


def edit_task(tasks, task_id, text):
    task = find_task(tasks, task_id)
    task["text"] = clean_text(text)
    return task


def delete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    tasks.remove(task)
    return task


def clear_done(tasks):
    """Remove all finished tasks. Returns how many were removed."""
    remaining = [task for task in tasks if not task["done"]]
    removed = len(tasks) - len(remaining)
    tasks[:] = remaining
    return removed


def filter_tasks(tasks, mode="all"):
    if mode == "all":
        return list(tasks)
    if mode == "pending":
        return [task for task in tasks if not task["done"]]
    if mode == "done":
        return [task for task in tasks if task["done"]]
    raise ValueError("Use: list, list pending, or list done.")


def format_task(task):
    mark = "x" if task["done"] else " "
    return f"{task['id']:>3}. [{mark}] {task['text']}"


def parse_id(text):
    try:
        return int(text)
    except ValueError:
        raise ValueError("The id must be a whole number, for example: done 2")


# ---------- Command handling ----------

def run_command(tasks, line, confirm=input):
    """Run one command. Returns (message, changed, quit)."""
    parts = line.strip().split(maxsplit=2)
    if not parts:
        return "", False, False

    command = parts[0].lower()
    arguments = line.strip()[len(parts[0]):].strip()

    if command in ("q", "quit", "exit"):
        return "Goodbye!", False, True

    if command == "help":
        return HELP_TEXT, False, False

    if command == "add":
        task = add_task(tasks, arguments)
        return f"Added task {task['id']}: {task['text']}", True, False

    if command == "list":
        mode = arguments.lower() or "all"
        shown = filter_tasks(tasks, mode)
        if not shown:
            return "No tasks to show.", False, False
        lines = [format_task(task) for task in shown]
        finished = sum(1 for task in tasks if task["done"])
        lines.append(f"({finished} of {len(tasks)} done)")
        return "\n".join(lines), False, False

    if command in ("done", "undone", "delete"):
        task_id = parse_id(arguments)
        if command == "delete":
            task = delete_task(tasks, task_id)
            return f"Deleted task {task['id']}: {task['text']}", True, False
        task = set_done(tasks, task_id, done=(command == "done"))
        state = "done" if task["done"] else "not done"
        return f"Task {task['id']} marked {state}: {task['text']}", True, False

    if command == "edit":
        edit_parts = arguments.split(maxsplit=1)
        if len(edit_parts) < 2:
            raise ValueError("Use: edit <id> <new text>, for example: edit 2 Buy bread")
        task = edit_task(tasks, parse_id(edit_parts[0]), edit_parts[1])
        return f"Task {task['id']} updated: {task['text']}", True, False

    if command == "clear":
        count = sum(1 for task in tasks if task["done"])
        if count == 0:
            return "No finished tasks to clear.", False, False
        answer = confirm(f"Delete {count} finished task(s)? (y/n): ").strip().lower()
        if answer != "y":
            return "Cancelled. Nothing was deleted.", False, False
        clear_done(tasks)
        return f"Deleted {count} finished task(s).", True, False

    raise ValueError(f"Unknown command '{command}'. Type 'help' to see the list.")


def main():
    tasks = load_tasks()
    print("To-Do List  (type 'help' for commands, 'q' to quit)")
    pending = len(filter_tasks(tasks, "pending"))
    print(f"You have {pending} unfinished task(s).")

    while True:
        line = input("> ")
        try:
            message, changed, should_quit = run_command(tasks, line)
        except ValueError as error:
            print(f"Error: {error}")
            continue

        if changed:
            save_tasks(tasks)
        if message:
            print(message)
        if should_quit:
            break


if __name__ == "__main__":
    main()
