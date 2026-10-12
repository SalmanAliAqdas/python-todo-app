"""Automated tests. Run with:  python -m unittest -v"""

import os
import tempfile
import unittest

import todo


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
        third = todo.add_task(self.tasks, "C")
        self.assertEqual(third["id"], 2)

    def test_empty_text_rejected(self):
        with self.assertRaises(ValueError):
            todo.add_task(self.tasks, "   ")

    def test_done_and_undone(self):
        todo.add_task(self.tasks, "Task")
        self.assertTrue(todo.set_done(self.tasks, 1)["done"])
        self.assertFalse(todo.set_done(self.tasks, 1, done=False)["done"])

    def test_edit(self):
        todo.add_task(self.tasks, "Old")
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

    def test_filter(self):
        todo.add_task(self.tasks, "A")
        todo.add_task(self.tasks, "B")
        todo.set_done(self.tasks, 1)
        self.assertEqual(len(todo.filter_tasks(self.tasks, "done")), 1)
        self.assertEqual(len(todo.filter_tasks(self.tasks, "pending")), 1)
        with self.assertRaises(ValueError):
            todo.filter_tasks(self.tasks, "nonsense")


class CommandTests(unittest.TestCase):
    def test_commands_work_end_to_end(self):
        tasks = []
        message, changed, _ = todo.run_command(tasks, "add Buy milk")
        self.assertTrue(changed)
        self.assertIn("Buy milk", message)
        todo.run_command(tasks, "done 1")
        self.assertTrue(tasks[0]["done"])
        todo.run_command(tasks, "edit 1 Buy bread")
        self.assertEqual(tasks[0]["text"], "Buy bread")

    def test_bad_input_raises_friendly_errors(self):
        tasks = []
        for bad in ["add", "done abc", "done 5", "edit 1", "dance"]:
            with self.assertRaises(ValueError, msg=bad):
                todo.run_command(tasks, bad)

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
            todo.add_task(tasks, "Urdu text: کتاب خریدیں")
            todo.save_tasks(tasks, path)
            self.assertEqual(todo.load_tasks(path), tasks)

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
