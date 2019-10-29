import sqlite3


class DatabaseTools:

    def __init__(self):

        self.db_name = 'notes_app.db'
        self.table_name = 'notes'

        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Создание таблицы
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} (name text, text text)')
        self.conn.commit()

    def drop_table(self):
        self.cursor.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        self.conn.commit()

    def add_note(self, note_name, note_text):
        data = (note_name, note_text)
        self.cursor.execute('INSERT INTO notes VALUES (?, ?)', data)
        self.conn.commit()

    def delete_note(self, note_name):
        note = (note_name,)
        self.cursor.execute('DELETE FROM notes WHERE name = ?', note)
        self.conn.commit()

    def update_note(self, new_note_name, note_text, old_note_name):
        data = (new_note_name, note_text, old_note_name)
        self.cursor.execute('UPDATE notes SET name = ?, text = ? WHERE name = ?', data)
        self.conn.commit()

    def get_note(self, note_name):
        note = (note_name,)
        self.cursor.execute('SELECT * FROM notes WHERE name = ?', note)
        note = self.cursor.fetchall()
        return note

    def get_all_notes(self):

        self.cursor.execute('SELECT * FROM notes')
        all_notes = self.cursor.fetchall()

        return all_notes
