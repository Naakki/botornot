import aiosqlite

class NotesDatabase:
    def __init__(self, db_path='notes.db'):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                comment TEXT,
                time TEXT NOT NULL,
                category TEXT
                )
            ''')
            await db.commit()
    
    async def add_note(self, data):
        title = data.get('title', '-')
        comment = data.get('comment', '-')
        category = data.get('category', '-')
        
        """Добавление заметки"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
            INSERT INTO notes (title, comment, time, category)
            VALUES (?, ?, datetime('now'), ?)
            ''', (title, comment, category))
            
            await db.commit()
            return cursor.lastrowid
    
    async def get_all_notes(self):
        """Получение всех заметок"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM notes ORDER BY time')
            notes = await cursor.fetchall()
            return [dict(note) for note in notes]
    
    async def get_note_by_id(self, note_id):
        """Получение заметки по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
            note = await cursor.fetchone()
            return dict(note) if note else None
    
    async def update_note(self, note_id, title, comment, category):
        """Обновление заметки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
            UPDATE notes 
            SET title = ?, comment = ?, category = ?, time = datetime('now')
            WHERE id = ?
            ''', (title, comment, category, note_id))
            await db.commit()
    
    async def delete_note(self, note_id):
        """Удаление заметки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            await db.commit()
    
    async def search_notes(self, query):
        """Поиск заметок"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
            SELECT * FROM notes 
            WHERE title LIKE ? OR comment LIKE ? OR category LIKE ?
            ORDER BY time DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            notes = await cursor.fetchall()
            return [dict(note) for note in notes]