import aiosqlite
from datetime import date, datetime, timedelta

class Database:
    def __init__(self, db_path="habits.db"):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    completed_date DATE NOT NULL,
                    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
                    UNIQUE(habit_id, completed_date)
                )
            """)
            await db.commit()

    async def add_habit(self, user_id: int, name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            await db.execute("INSERT INTO habits (user_id, name) VALUES (?, ?)", (user_id, name))
            await db.commit()

    async def get_habits(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchall()

    async def delete_habit(self, habit_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            await db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            await db.commit()

    async def mark_completed(self, habit_id: int, completed_date: date):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            try:
                await db.execute(
                    "INSERT INTO completions (habit_id, completed_date) VALUES (?, ?)",
                    (habit_id, completed_date.isoformat())
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def is_completed_today(self, habit_id: int, today: date):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            async with db.execute(
                "SELECT 1 FROM completions WHERE habit_id = ? AND completed_date = ?",
                (habit_id, today.isoformat())
            ) as cursor:
                return await cursor.fetchone() is not None

    async def get_habit_stats(self, habit_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON;")
            db.row_factory = aiosqlite.Row

            # Get all completion dates for this habit, ordered descending
            async with db.execute(
                "SELECT completed_date FROM completions WHERE habit_id = ? ORDER BY completed_date DESC",
                (habit_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                completion_dates = [date.fromisoformat(row['completed_date']) for row in rows]

            if not completion_dates:
                return {
                    "current_streak": 0,
                    "best_streak": 0,
                    "total_completions": 0,
                    "completion_rate": 0
                }

            # Calculate streaks
            current_streak = 0
            today = date.today()
            yesterday = today - timedelta(days=1)

            # Check if streak is still active (completed today or yesterday)
            if completion_dates[0] == today or completion_dates[0] == yesterday:
                current_streak = 1
                for i in range(len(completion_dates) - 1):
                    if completion_dates[i] - completion_dates[i+1] == timedelta(days=1):
                        current_streak += 1
                    else:
                        break

            best_streak = 0
            temp_streak = 0
            if completion_dates:
                temp_streak = 1
                best_streak = 1
                for i in range(len(completion_dates) - 1):
                    if completion_dates[i] - completion_dates[i+1] == timedelta(days=1):
                        temp_streak += 1
                    else:
                        best_streak = max(best_streak, temp_streak)
                        temp_streak = 1
                best_streak = max(best_streak, temp_streak)

            # Completion rate since creation
            async with db.execute("SELECT created_at FROM habits WHERE id = ?", (habit_id,)) as cursor:
                habit_row = await cursor.fetchone()
                # Handle potential space instead of T in timestamp (older python versions compatibility)
                created_at_str = habit_row[0].replace(" ", "T")
                created_at = datetime.fromisoformat(created_at_str).date()

            days_since_creation = (today - created_at).days + 1
            total_completions = len(completion_dates)
            completion_rate = (total_completions / days_since_creation) * 100

            return {
                "current_streak": current_streak,
                "best_streak": best_streak,
                "total_completions": total_completions,
                "completion_rate": round(completion_rate, 2)
            }
