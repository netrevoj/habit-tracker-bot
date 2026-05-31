import unittest
import asyncio
import os
from datetime import date, timedelta, datetime
from database.db import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_habits.db"
        self.db = Database(self.db_path)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.db.init())

    def tearDown(self):
        self.loop.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_and_get_habits(self):
        async def run():
            user_id = 123
            await self.db.add_habit(user_id, "Habit 1")
            await asyncio.sleep(1.1) # Ensure different timestamps
            await self.db.add_habit(user_id, "Habit 2")

            habits = await self.db.get_habits(user_id)
            self.assertEqual(len(habits), 2)
            # Should be sorted by created_at DESC
            self.assertEqual(habits[0]['name'], "Habit 2")
            self.assertEqual(habits[1]['name'], "Habit 1")

        self.loop.run_until_complete(run())

    def test_mark_and_is_completed(self):
        async def run():
            user_id = 123
            await self.db.add_habit(user_id, "Habit 1")
            habits = await self.db.get_habits(user_id)
            habit_id = habits[0]['id']

            today = date.today()
            is_done = await self.db.is_completed_today(habit_id, today)
            self.assertFalse(is_done)

            success = await self.db.mark_completed(habit_id, today)
            self.assertTrue(success)

            is_done = await self.db.is_completed_today(habit_id, today)
            self.assertTrue(is_done)

            # Second time should fail (Unique constraint)
            success = await self.db.mark_completed(habit_id, today)
            self.assertFalse(success)

        self.loop.run_until_complete(run())

    def test_remove_completion(self):
        async def run():
            user_id = 123
            await self.db.add_habit(user_id, "Habit 1")
            habits = await self.db.get_habits(user_id)
            habit_id = habits[0]['id']
            today = date.today()

            await self.db.mark_completed(habit_id, today)
            self.assertTrue(await self.db.is_completed_today(habit_id, today))

            await self.db.remove_completion(habit_id, today)
            self.assertFalse(await self.db.is_completed_today(habit_id, today))

        self.loop.run_until_complete(run())

    def test_streaks(self):
        async def run():
            user_id = 123
            await self.db.add_habit(user_id, "Habit 1")
            habits = await self.db.get_habits(user_id)
            habit_id = habits[0]['id']

            today = date.today()
            yesterday = today - timedelta(days=1)
            day_before = today - timedelta(days=2)

            # Mark yesterday and day before
            await self.db.mark_completed(habit_id, yesterday)
            await self.db.mark_completed(habit_id, day_before)

            stats = await self.db.get_habit_stats(habit_id)
            self.assertEqual(stats['current_streak'], 2)
            self.assertEqual(stats['best_streak'], 2)

            # Mark today
            await self.db.mark_completed(habit_id, today)
            stats = await self.db.get_habit_stats(habit_id)
            self.assertEqual(stats['current_streak'], 3)
            self.assertEqual(stats['best_streak'], 3)

            # Mark a week ago (broken streak)
            last_week = today - timedelta(days=7)
            await self.db.mark_completed(habit_id, last_week)

            stats = await self.db.get_habit_stats(habit_id)
            self.assertEqual(stats['current_streak'], 3)
            self.assertEqual(stats['best_streak'], 3)
            self.assertEqual(stats['total_completions'], 4)

        self.loop.run_until_complete(run())

if __name__ == "__main__":
    unittest.main()
