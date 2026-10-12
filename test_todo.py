"""Automated tests. Run with:  python -m unittest -v"""

import json
import os
import tempfile
import unittest
from datetime import date

import todo

TODAY = date(2026, 10, 15)


class TaskOperationTests(unittest.TestCase):
    def setUp(self):
        self.tasks = []

    def test_add_gives_increasing_ids(self):
        first = todo.add_task(self.tasks, "Buy milk")
        second = todo.add_task(self.tasks, "Call Ali")
        self.assertEqual((first["id"], second["id"]), (1, 2))

    def test_new_id_is_one_more_than_highest_existing_id(self):
        todo.add_task(self.tasks, "A")
        todo.add_task(self.tasks, "B")
        todo.delete_task(self.tasks, 2)
        self.assertEqual(todo.add_task(self.tasks, "C")["id"], 2)

    def test_empty_text_rejected(self):
        with self.assertRaises(ValueError):
            todo.add_task(self.tasks, "   ")

    def test_done_undone_edit(self):
        todo.add_task(self.tasks, "Old")
        self.assertTrue(todo.set_done(self.tasks, 1)["done"])
        self.assertFalse(todo.set_done(self.tasks, 1, done=False)["done"])
        todo.edit_task(self.tasks, 1, "New")
        self.assertEqual(self.tasks[0]["text"], "New")

    def test_missing_id(self):
        with self.assertRaises(ValueError):
            todo.set_done(self.tasks, 99)

    def test_clear_done(self):
        todo.add_task(self.tasks, "A")
        todo.add_task(self.tasks, "B")
        todo.set_done(self.tasks, 1)
        self.assertEqual(todo.clear_done(self.tasks), 1)
        self.assertEqual([t["text"] for t in self.tasks], ["B"])


class PriorityAndDueTests(unittest.TestCase):
    def test_parse_add_input(self):
        text, priority, due = todo.parse_add_input("Pay bill !high @tomorrow", TODAY)
        self.assertEqual((text, priority, due), ("Pay bill", "high", "2026-10-16"))

    def test_parse_add_input_defaults(self):
        self.assertEqual(todo.parse_add_input("Buy milk", TODAY), ("Buy milk", "normal", None))

    def test_flags_can_come_first_or_last(self):
        text, priority, due = todo.parse_add_input("@2026-12-01 !low Read book", TODAY)
        self.assertEqual((text, priority, due), ("Read book", "low", "2026-12-01"))

    def test_bad_priority_and_dates(self):
        for bad in ["Task !urgent", "Task @31-12-2026", "Task @2026-02-30", "Task @soon"]:
            with self.assertRaises(ValueError, msg=bad):
                todo.parse_add_input(bad, TODAY)

    def test_today_and_tomorrow(self):
        self.assertEqual(todo.parse_due("today", TODAY), "2026-10-15")
        self.assertEqual(todo.parse_due("Tomorrow", TODAY), "2026-10-16")

    def test_set_due_and_remove(self):
        tasks = []
        todo.add_task(tasks, "A")
        todo.set_due(tasks, 1, "2026-11-01", TODAY)
        self.assertEqual(tasks[0]["due"], "2026-11-01")
        todo.set_due(tasks, 1, "none", TODAY)
        self.assertIsNone(tasks[0]["due"])

    def test_set_priority(self):
        tasks = []
        todo.add_task(tasks, "A")
        todo.set_priority(tasks, 1, "HIGH")
        self.assertEqual(tasks[0]["priority"], "high")
        with self.assertRaises(ValueError):
            todo.set_priority(tasks, 1, "urgent")


class FilterSearchStatsTests(unittest.TestCase):
    def setUp(self):
        self.tasks = []
        todo.add_task(self.tasks, "Old bill", "high", "2026-10-10")      # 1 overdue
        todo.add_task(self.tasks, "Today job", "normal", "2026-10-15")   # 2 due today
        todo.add_task(self.tasks, "Later job", "low", "2026-11-01")      # 3
        todo.add_task(self.tasks, "Finished old", "normal", "2026-10-01")  # 4
        todo.set_done(self.tasks, 4)

    def ids(self, mode):
        return [t["id"] for t in todo.filter_tasks(self.tasks, mode, TODAY)]

    def test_filters(self):
        self.assertEqual(self.ids("all"), [1, 2, 3, 4])
        self.assertEqual(self.ids("pending"), [1, 2, 3])
        self.assertEqual(self.ids("done"), [4])
        self.assertEqual(self.ids("overdue"), [1])   # done task 4 is not overdue
        self.assertEqual(self.ids("today"), [2])
        self.assertEqual(self.ids("high"), [1])
        with self.assertRaises(ValueError):
            self.ids("nonsense")

    def test_search_is_case_insensitive(self):
        self.assertEqual([t["id"] for t in todo.search_tasks(self.tasks, "JOB")], [2, 3])
        self.assertEqual(todo.search_tasks(self.tasks, "zzz"), [])
        with self.assertRaises(ValueError):
            todo.search_tasks(self.tasks, "  ")

    def test_stats(self):
        stats = todo.get_stats(self.tasks, TODAY)
        self.assertEqual(stats, {"total": 4, "done": 1, "pending": 3, "overdue": 1, "high": 1, "percent": 25})

    def test_stats_empty_list(self):
        self.assertEqual(todo.get_stats([], TODAY)["percent"], 0)

    def test_format_shows_details(self):
        line = todo.format_task(self.tasks[0], TODAY)
        self.assertIn("!high", line)
        self.assertIn("due 2026-10-10", line)
        self.assertIn("OVERDUE", line)
        self.assertNotIn("OVERDUE", todo.format_task(self.tasks[3], TODAY))


class CommandTests(unittest.TestCase):
    def test_commands_end_to_end(self):
        tasks = []
        message, changed, _ = todo.run_command(tasks, "add Buy milk !high @tomorrow", today=TODAY)
        self.assertTrue(changed)
        self.assertEqual(tasks[0]["priority"], "high")
        self.assertEqual(tasks[0]["due"], "2026-10-16")
        todo.run_command(tasks, "priority 1 low", today=TODAY)
        todo.run_command(tasks, "due 1 2026-12-25", today=TODAY)
        self.assertEqual((tasks[0]["priority"], tasks[0]["due"]), ("low", "2026-12-25"))
        todo.run_command(tasks, "done 1", today=TODAY)
        self.assertTrue(tasks[0]["done"])
        self.assertIn("Total: 1", todo.run_command(tasks, "stats", today=TODAY)[0])
        self.assertIn("Buy milk", todo.run_command(tasks, "search milk", today=TODAY)[0])

    def test_bad_input_raises_friendly_errors(self):
        tasks = []
        todo.add_task(tasks, "A")
        for bad in ["add", "add !high", "done abc", "done 5", "edit 1", "priority 1",
                    "priority 1 urgent", "due 1 soon", "due 1", "search", "list weird", "dance"]:
            with self.assertRaises(ValueError, msg=bad):
                todo.run_command(tasks, bad, today=TODAY)

    def test_clear_asks_first(self):
        tasks = []
        todo.add_task(tasks, "A")
        todo.set_done(tasks, 1)
        todo.run_command(tasks, "clear", confirm=lambda prompt: "n")
        self.assertEqual(len(tasks), 1)
        todo.run_command(tasks, "clear", confirm=lambda prompt: "y")
        self.assertEqual(len(tasks), 0)

    def test_quit(self):
        self.assertTrue(todo.run_command([], "q")[2])


class SaveLoadTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tasks.json")
            tasks = []
            todo.add_task(tasks, "Urdu text: کتاب خریدیں", "high", "2026-12-01")
            todo.save_tasks(tasks, path)
            self.assertEqual(todo.load_tasks(path), tasks)

    def test_version_1_file_still_loads(self):
        old_format = [{"id": 1, "text": "Old task", "done": True, "created": "2026-10-12"}]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tasks.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump(old_format, file)
            tasks = todo.load_tasks(path)
            self.assertEqual(tasks[0]["priority"], "normal")
            self.assertIsNone(tasks[0]["due"])
            self.assertTrue(tasks[0]["done"])

    def test_missing_file_gives_empty_list(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(todo.load_tasks(os.path.join(folder, "none.json")), [])

    def test_damaged_file_is_backed_up(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tasks.json")
            with open(path, "w") as file:
                file.write("{ not valid json")
            self.assertEqual(todo.load_tasks(path), [])
            self.assertTrue(os.path.exists(path + ".broken"))


if __name__ == "__main__":
    unittest.main()
