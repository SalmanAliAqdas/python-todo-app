"""Command-line to-do list app, version 2.

Features: priorities, due dates, search, statistics and automatic saving.
Tasks are saved in tasks.json next to this script.
Type 'help' to see all commands.
"""

import json
import os
from datetime import date, timedelta

DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")
PRIORITIES = ("high", "normal", "low")

HELP_TEXT = """\
Adding tasks (priority and due date are optional, put them anywhere):
  add Buy milk
  add Pay bill !high @2026-10-20
  add Call Ali !low @tomorrow
  (priority: !high !normal !low   date: @today @tomorrow @YYYY-MM-DD)

Viewing:
  list                show all tasks
  list pending        unfinished tasks
  list done           finished tasks
  list overdue        unfinished tasks past their due date
  list today          unfinished tasks due today
  list high           unfinished high-priority tasks
  search <word>       find tasks containing a word
  stats               show a summary

Changing:
  done <id>           mark as done          e.g.  done 2
  undone <id>         mark as not done
  edit <id> <text>    change the text       e.g.  edit 2 Buy bread
  priority <id> <p>   set priority          e.g.  priority 2 high
  due <id> <date>     set due date          e.g.  due 2 tomorrow   (or: due 2 none)
  delete <id>         delete a task
  clear               delete all finished tasks (asks first)

Other:
  help                show this message
  q                   quit"""


# ---------- Saving and loading ----------

def normalize(task):
    """Fill in missing fields so tasks saved by version 1 still work."""
    task.setdefault("priority", "normal")
    task.setdefault("due", None)
    task.setdefault("done", False)
    task.setdefault("created", "")
    return task


def load_tasks(path=DEFAULT_FILE):
    """Read tasks from disk. Returns an empty list if there is no file yet."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("unexpected file format")
        return [normalize(task) for task in data]
    except (json.JSONDecodeError, ValueError, TypeError, KeyError):
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


# ---------- Dates and parsing ----------

def parse_due(text, today=None):
    """Turn 'today', 'tomorrow' or 'YYYY-MM-DD' into a date string."""
    today = today or date.today()
    text = text.strip().lower()
    if text == "today":
        return today.isoformat()
    if text == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValueError(f"'{text}' is not a valid date. Use today, tomorrow or YYYY-MM-DD.")


def parse_priority(text):
    text = text.strip().lower()
    if text not in PRIORITIES:
        raise ValueError("Priority must be high, normal or low.")
    return text


def parse_add_input(arguments, today=None):
    """Split 'Pay bill !high @tomorrow' into (text, priority, due)."""
    words, priority, due = [], "normal", None
    for word in arguments.split():
        if word.startswith("!") and len(word) > 1:
            priority = parse_priority(word[1:])
        elif word.startswith("@") and len(word) > 1:
            due = parse_due(word[1:], today)
        else:
            words.append(word)
    return " ".join(words), priority, due


def parse_id(text):
    try:
        return int(text)
    except ValueError:
        raise ValueError("The id must be a whole number, for example: done 2")


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


def add_task(tasks, text, priority="normal", due=None):
    text = clean_text(text)
    new_id = max((task["id"] for task in tasks), default=0) + 1
    task = {
        "id": new_id,
        "text": text,
        "done": False,
        "created": date.today().isoformat(),
        "priority": priority,
        "due": due,
    }
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


def set_priority(tasks, task_id, priority):
    task = find_task(tasks, task_id)
    task["priority"] = parse_priority(priority)
    return task


def set_due(tasks, task_id, due_text, today=None):
    task = find_task(tasks, task_id)
    if due_text.strip().lower() in ("none", "clear", "remove"):
        task["due"] = None
    else:
        task["due"] = parse_due(due_text, today)
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


def is_overdue(task, today=None):
    today = today or date.today()
    return (not task["done"]) and task["due"] is not None and task["due"] < today.isoformat()


def filter_tasks(tasks, mode="all", today=None):
    today = today or date.today()
    if mode == "all":
        return list(tasks)
    if mode == "pending":
        return [t for t in tasks if not t["done"]]
    if mode == "done":
        return [t for t in tasks if t["done"]]
    if mode == "overdue":
        return [t for t in tasks if is_overdue(t, today)]
    if mode == "today":
        return [t for t in tasks if not t["done"] and t["due"] == today.isoformat()]
    if mode == "high":
        return [t for t in tasks if not t["done"] and t["priority"] == "high"]
    raise ValueError("Use: list, list pending, list done, list overdue, list today or list high.")


def search_tasks(tasks, word):
    word = word.strip().lower()
    if not word:
        raise ValueError("Type a word to search for, for example: search milk")
    return [t for t in tasks if word in t["text"].lower()]


def get_stats(tasks, today=None):
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    return {
        "total": total,
        "done": done,
        "pending": total - done,
        "overdue": len(filter_tasks(tasks, "overdue", today)),
        "high": len(filter_tasks(tasks, "high", today)),
        "percent": round(100 * done / total) if total else 0,
    }


def format_task(task, today=None):
    mark = "x" if task["done"] else " "
    line = f"{task['id']:>3}. [{mark}] {task['text']}"
    if task["priority"] != "normal":
        line += f"  !{task['priority']}"
    if task["due"]:
        line += f"  (due {task['due']})"
    if is_overdue(task, today):
        line += "  OVERDUE"
    return line


# ---------- Command handling ----------

def run_command(tasks, line, confirm=input, today=None):
    """Run one command. Returns (message, changed, quit)."""
    stripped = line.strip()
    if not stripped:
        return "", False, False

    parts = stripped.split(maxsplit=1)
    command = parts[0].lower()
    arguments = parts[1].strip() if len(parts) > 1 else ""

    if command in ("q", "quit", "exit"):
        return "Goodbye!", False, True

    if command == "help":
        return HELP_TEXT, False, False

    if command == "add":
        text, priority, due = parse_add_input(arguments, today)
        task = add_task(tasks, text, priority, due)
        return f"Added task {task['id']}: {format_task(task, today).split('. ', 1)[1]}", True, False

    if command == "list":
        shown = filter_tasks(tasks, arguments.lower() or "all", today)
        if not shown:
            return "No tasks to show.", False, False
        lines = [format_task(task, today) for task in shown]
        finished = sum(1 for task in tasks if task["done"])
        lines.append(f"({finished} of {len(tasks)} done)")
        return "\n".join(lines), False, False

    if command == "search":
        found = search_tasks(tasks, arguments)
        if not found:
            return "No tasks match that word.", False, False
        return "\n".join(format_task(task, today) for task in found), False, False

    if command == "stats":
        s = get_stats(tasks, today)
        return (
            f"Total: {s['total']}   Done: {s['done']} ({s['percent']}%)   "
            f"Pending: {s['pending']}\n"
            f"Overdue: {s['overdue']}   High priority pending: {s['high']}"
        ), False, False

    if command in ("done", "undone", "delete"):
        task_id = parse_id(arguments)
        if command == "delete":
            task = delete_task(tasks, task_id)
            return f"Deleted task {task['id']}: {task['text']}", True, False
        task = set_done(tasks, task_id, done=(command == "done"))
        state = "done" if task["done"] else "not done"
        return f"Task {task['id']} marked {state}: {task['text']}", True, False

    if command in ("edit", "priority", "due"):
        pieces = arguments.split(maxsplit=1)
        if len(pieces) < 2:
            examples = {
                "edit": "edit 2 Buy bread",
                "priority": "priority 2 high",
                "due": "due 2 tomorrow",
            }
            raise ValueError(f"Use: {examples[command]}")
        task_id, value = parse_id(pieces[0]), pieces[1]
        if command == "edit":
            task = edit_task(tasks, task_id, value)
            return f"Task {task['id']} updated: {task['text']}", True, False
        if command == "priority":
            task = set_priority(tasks, task_id, value)
            return f"Task {task['id']} priority is now {task['priority']}.", True, False
        task = set_due(tasks, task_id, value, today)
        due_text = task["due"] if task["due"] else "none"
        return f"Task {task['id']} due date is now {due_text}.", True, False

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
    print("To-Do List v2  (type 'help' for commands, 'q' to quit)")
    stats = get_stats(tasks)
    print(f"You have {stats['pending']} unfinished task(s), {stats['overdue']} overdue.")

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
