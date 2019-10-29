import sys

import time

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget, \
    QListWidget, QTextEdit, QLineEdit, QMessageBox, QVBoxLayout, QHBoxLayout, QDesktopWidget, QMainWindow

from db import DatabaseTools


class OpenWindow(QWidget):

    def __init__(self, parent, note_name):
        super().__init__()

        self.parent = parent
        self.note_name = note_name

        self.vbox = QVBoxLayout()

        self.add_line_edit()
        self.add_text_edit()
        self.add_button()

        self.setLayout(self.vbox)
        self.setMinimumSize(QSize(500, 250))
        self.setWindowTitle('Редактировние заметки')
        self.show()

    def add_line_edit(self):
        self.line_edit = QLineEdit()
        self.line_edit.insert(self.note_name)

        self.vbox.addWidget(self.line_edit)

    def add_text_edit(self):
        self.text_edit = QTextEdit()

        note = self.parent.db.get_note(self.note_name)
        init_text = note[0][1]

        self.text_edit.insertPlainText(init_text)

        self.vbox.addWidget(self.text_edit)

    def add_button(self):
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.clicked.connect(self.save_button_clicked)

        self.vbox.addWidget(self.save_button)

    def save_button_clicked(self):
        new_note_name = self.line_edit.text()

        all_notes = self.parent.db.get_all_notes()
        notes_names = {note[0] for note in all_notes}

        if new_note_name in notes_names and new_note_name != self.note_name:
            msg = QMessageBox()
            msg.addButton('ОК', QMessageBox.AcceptRole)
            msg.setWindowTitle('Конфликт имен')
            msg.setText('Имя ' + new_note_name + ' уже существует! Выбирете другое имя')
            msg.exec_()
            return

        note_text = self.text_edit.toPlainText()

        self.parent.db.update_note(new_note_name=new_note_name,
                                   note_text=note_text,
                                   old_note_name=self.note_name)

        item = self.parent.notes_list_widget.currentItem()
        item.setText(new_note_name)
        self.parent.notes_list_widget.setCurrentItem(item)
        self.close()

    def closeEvent(self, QCloseEvent):
        self.parent.notes_list_widget.setDisabled(False)
        super().closeEvent(QCloseEvent)


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.db = DatabaseTools()

        self.initUI()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.hbox_search = QHBoxLayout()
        self.hbox_buttons = QHBoxLayout()

        self.add_search()
        self.add_notes_list_widget()
        self.show_all_notes()
        self.add_control_buttons()

        self.setLayout(self.vbox)
        self.setMinimumSize(QSize(400, 300))
        self.setWindowTitle('Заметки')
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def show_all_notes(self):
        all_notes = self.db.get_all_notes()
        notes_names = [note[0] for note in all_notes]
        self.notes_list_widget.addItems(notes_names)

    def add_search(self):
        self.search_line = QLineEdit(self)
        self.search_line.setPlaceholderText('Поиск по названию')
        self.search_line.returnPressed.connect(self.search_line_return_pressed)

        self.vbox.addWidget(self.search_line)

    def search_line_return_pressed(self):

        text = self.search_line.text()

        if not text:
            self.show_all_notes()

        all_notes = self.db.get_all_notes()

        notes = [note[0] for note in all_notes if text in note[0]]

        self.notes_list_widget.clear()
        self.notes_list_widget.addItems(notes)

    def add_notes_list_widget(self):
        self.notes_list_widget = QListWidget(self)
        self.notes_list_widget.setUniformItemSizes(True)
        self.notes_list_widget.itemDoubleClicked.connect(self.list_item_clicked)

        self.vbox.addWidget(self.notes_list_widget)

    def add_control_buttons(self):
        self.new_button = QPushButton('Добавить', self)
        self.delete_button = QPushButton('Удалить', self)

        self.new_button.clicked.connect(self.new_button_clicked)
        self.delete_button.clicked.connect(self.delete_button_clicked)

        self.hbox_buttons.addWidget(self.new_button)
        self.hbox_buttons.addWidget(self.delete_button)

        self.vbox.addLayout(self.hbox_buttons)

    def new_button_clicked(self):
        now = time.ctime()

        note_number = self.notes_list_widget.count() + 1
        note_name = str(note_number) + ' ' + now

        self.db.add_note(note_name=note_name, note_text='Текст заметки')

        self.notes_list_widget.addItem(note_name)

    def list_item_clicked(self):
        item = self.notes_list_widget.currentItem()
        if not item:
            return
        note_name = item.text()
        self.open = OpenWindow(self, note_name)
        self.notes_list_widget.setDisabled(True)

    def delete_button_clicked(self):
        row = self.notes_list_widget.currentRow()
        if row == -1:
            return
        text = self.notes_list_widget.currentItem().text()

        msg = QMessageBox()
        msg.addButton('Да', QMessageBox.AcceptRole)
        msg.addButton('Нет', QMessageBox.RejectRole)
        msg.setText('Удалить запись ' + text + '?')

        reply = msg.exec_()
        if reply == 1:
            return

        self.db.delete_note(text)

        self.notes_list_widget.takeItem(row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
