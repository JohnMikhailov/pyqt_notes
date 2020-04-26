import sqlite3


class DatabaseTools:  # класс для работы с базой данных

    '''
            запрос  CREATE TABLE IF NOT EXISTS notes (name text, text text)

            создает такую таблицу (если такой таблицы еще нет, а если есть, то не создает)

            __________________
            |    notes       |
            ------------------
            |id | name | text|
            ------------------


            например, если сделать запрос: INSERT INTO notes VALUES (заметка 1, текст заметки 1), то данные
            в базе данных будут выглядеть так:

            ___________________________________
            |            notes                |
            -----------------------------------
            |id | name      | text            |
            -----------------------------------
            | 1 | заметка 1 | текст заметки 1 |
            -----------------------------------
    '''

    def __init__(self):

        self.db_name = 'notes_app.db'
        self.table_name = 'notes'

        self.conn = sqlite3.connect(self.db_name)  # подключаемся к базе
        self.cursor = self.conn.cursor()  # создаем курсор (специальный объект) для общения с базой

        # метод execute выполняет SQL запрос

        # создаем таблицу
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} (name text, text text)')
        self.conn.commit()  # сохраняем изменения

    def drop_table(self):  # можно использовать, если нужно удалить таблицу
        self.cursor.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        self.conn.commit()

    def add_note(self, note_name, note_text):  # добавляем заметку в базу данных
        # перед добавлением данные нужно засунуть в кортеж, потому что sqlite3 работает с кортежами
        data = (note_name, note_text)
        # вместо знаков вопроса '?' подставятся значения из кортежа data
        # то есть вместо первого вопроса подставится первое значение в кортеже
        # а вместо второго впороса подставится второе значение из кортежа
        # например, если data = ('заметка', 'текст'), то запрос к бд будет выглядеть так:
        # 'INSERT INTO notes VALUES ('заметка', 'текст')
        self.cursor.execute('INSERT INTO notes VALUES (?, ?)', data)
        self.conn.commit()

    def delete_note(self, note_name):  # удаляем заметку
        note = (note_name,)
        self.cursor.execute('DELETE FROM notes WHERE name = ?', note)
        self.conn.commit()

    def update_note(self, new_note_name, note_text, old_note_name):  # обновляем заметку
        data = (new_note_name, note_text, old_note_name)
        self.cursor.execute('UPDATE notes SET name = ?, text = ? WHERE name = ?', data)
        self.conn.commit()

    def get_note(self, note_name):  # находим заметку в таблице по ее названию
        note = (note_name,)
        self.cursor.execute('SELECT * FROM notes WHERE name = ?', note)
        note = self.cursor.fetchall()
        return note

    def get_all_notes(self):  # достаем из таблицы все заметки

        self.cursor.execute('SELECT * FROM notes')
        all_notes = self.cursor.fetchall()

        return all_notes  # возвращается список кортежей, пример:
        # [('имя заметки 1', 'текст заметки 1'), ('имя заметки 2', 'текст заметки 2')]
        # это пример, когда в таблице у нас всего две записи
