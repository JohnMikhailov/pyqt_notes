import sys

import time

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget, \
    QListWidget, QTextEdit, QLineEdit, QMessageBox, QVBoxLayout, QHBoxLayout, QDesktopWidget

from db import DatabaseTools


class OpenWindow(QWidget):  # создаем класс для виджета редактирования заметки
    # наследуемся от класса QWidget, чтобы использовать весь его функционал и дополнить своим

    def __init__(self, parent, note_name):
        super().__init__()

        self.parent = parent  # это объект, который вызывает объект этого класса
        # таким образом нам доступны все атрибуты объекта parent
        # мы передаем весь объект, потому что так удобнее обращаться к необходимым нам полям

        """
           ВАЖНО: все объекты в python измненяемые - это значит, что если мы тут изменим 
           поля объекта parent, то они будут изменены вне объекта этого класса
        """

        self.note_name = note_name  # имя заметки, которую выбрали в списке - передаем ее как параметр

        self.vbox = QVBoxLayout()  # этот объект позволит нам расположить элементы в нужном порядке,
        # например QVBoxLayout позволяет добавлять элементы друг на друга
        # то есть если мы добавляем сначала строку ввода текста, а потом кнопку, то на экране
        # сверху будет строка ввода текста, а под ней - кнопка

        # добавляем на экран элементы интерфейса
        self.add_line_edit()
        self.add_text_edit()
        self.add_button()

        self.setLayout(self.vbox)  # устанавливаем расположение элементов
        self.setMinimumSize(QSize(500, 250))
        self.setWindowTitle('Редактирование заметки')
        self.show()

    def add_line_edit(self):
        self.line_edit = QLineEdit()
        self.line_edit.insert(self.note_name)

        self.vbox.addWidget(self.line_edit)  # добавляем виджет редактирования строки

    def add_text_edit(self):
        self.text_edit = QTextEdit()

        note = self.parent.db.get_note(self.note_name)
        init_text = note[0][1]

        self.text_edit.insertPlainText(init_text)

        self.vbox.addWidget(self.text_edit)

    def add_button(self):  # добавляем кнопку сохранения
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.clicked.connect(self.save_button_clicked)  # назначаем обработчик (слот) для события (сигнала)

        self.vbox.addWidget(self.save_button)

    def save_button_clicked(self):  # обработка нажатия кнопки 'Сохранить'

        # здесь просто достаем имя заметки и текст заметки и сохраняем их в базе

        new_note_name = self.line_edit.text()

        all_notes = self.parent.db.get_all_notes()
        notes_names = {note[0] for note in all_notes}

        # проверяем, есть ли среди имен заметок имя, которое мы сейчас ввели (new_note_name in notes_names)
        # и также проверяем, изменилось ли оно (new_note_name != self.note_name)
        if new_note_name in notes_names and new_note_name != self.note_name:
            # если такое имя уже есть, то выводим сообщение
            msg = QMessageBox()
            msg.addButton('ОК', QMessageBox.AcceptRole)
            msg.setWindowTitle('Конфликт имен')
            msg.setText('Имя ' + new_note_name + ' уже существует! Выберите другое имя')
            msg.exec_()
            return  # завершаем выполнение метода

        # если условие выше НЕ выполнилось, то тогда этот код ниже будет выполнен

        note_text = self.text_edit.toPlainText()  # получаем текст заметки

        # обновляем заметку в базе
        self.parent.db.update_note(new_note_name=new_note_name,
                                   note_text=note_text,
                                   old_note_name=self.note_name)

        # обновляем имя заметки в списке на экране
        item = self.parent.notes_list_widget.currentItem()  # получаем выбранный элемент в списке
        item.setText(new_note_name)  # меняем текст элемента
        self.parent.notes_list_widget.setCurrentItem(item)  # устанавливаем изменения на выбранном элементе
        self.close()  # закрываем окно редактирования заметки (закрываем текущий виджет)

    def closeEvent(self, QCloseEvent):  # переопределяем метод
        # делаем доступным список заметок на экране
        # его нужно отключать, чтобы нельзя было сохранить текст заметки в другой заметке
        self.parent.setDisabled(False)
        super().closeEvent(QCloseEvent)  # вызываем базовый метод - это правило хорошего тона


class MainWindow(QWidget):  # главный экран

    # MainWindow - это parent для OpenWindow

    # этот виджет отображает список заметок, кнопку добавления заметки и кнопку удаления выбранной заметки

    def __init__(self):
        super(MainWindow, self).__init__()

        self.db = DatabaseTools()  # создаем объект, с помощью которого мы будем общаться с базой

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
        self.center()  # распологаем окно в центре экрана

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def show_all_notes(self):  # отображаем на экране все заметки из базы
        all_notes = self.db.get_all_notes()
        notes_names = [note[0] for note in all_notes]
        self.notes_list_widget.addItems(notes_names)

    def add_search(self):  # добавляем на экран поисковую строку
        self.search_line = QLineEdit(self)
        self.search_line.setPlaceholderText('Поиск по названию')
        # поиск заработает, если нажать Enter, это мы и указываем ниже и назначаем обработчик
        self.search_line.returnPressed.connect(self.search_line_return_pressed)

        self.vbox.addWidget(self.search_line)

    def search_line_return_pressed(self):  # когда на поисковой строке будет нажат Enter, то сработает этот метод

        text = self.search_line.text()

        if not text:  # если никакого текста не введено, то отображаем все заметки
            self.show_all_notes()

        all_notes = self.db.get_all_notes()  # достаем все заметки из базы данных

        # собираем имена заметок, потому что именно их мы будем отображать на главном экране
        notes = [note[0] for note in all_notes if text in note[0]]

        self.notes_list_widget.clear()  # очищаем список
        self.notes_list_widget.addItems(notes)  # заносим инфу в список

    def add_notes_list_widget(self):  # добавляем список заметок на экран
        self.notes_list_widget = QListWidget(self)
        self.notes_list_widget.setUniformItemSizes(True)  # все названия элементов списка будут равны по длинне

        # если по элементу списка кликнуть два раза, то открываем окно редактирования выбранной заметки
        self.notes_list_widget.itemDoubleClicked.connect(self.list_item_clicked)

        self.vbox.addWidget(self.notes_list_widget)

    def add_control_buttons(self):  # добавляем на экран кнопки управдения
        self.new_button = QPushButton('Добавить', self)
        self.delete_button = QPushButton('Удалить', self)

        self.new_button.clicked.connect(self.new_button_clicked)
        self.delete_button.clicked.connect(self.delete_button_clicked)

        self.hbox_buttons.addWidget(self.new_button)
        self.hbox_buttons.addWidget(self.delete_button)

        self.vbox.addLayout(self.hbox_buttons)

    def new_button_clicked(self):
        now = time.ctime()  # получаем текущее время

        note_number = self.notes_list_widget.count() + 1  # получаем число заметок на экране
        note_name = str(note_number) + ' ' + now  # создаем имя заметки по умолчанию

        # сохраняем в базе только что созданную заметку с текстом по умолчанию
        self.db.add_note(note_name=note_name, note_text='Текст заметки')

        self.notes_list_widget.addItem(note_name)  # добавляем имя заметки на экран

    def list_item_clicked(self):  # если на элемент списка кликнуть два раза, то сработает этот метод
        item = self.notes_list_widget.currentItem()
        if not item:
            return
        note_name = item.text()
        self.open = OpenWindow(self, note_name)  # открываем окно редактирования заметки
        self.setDisabled(True)

    def delete_button_clicked(self):  # этот метод вызовется, когда будет нажата конпка 'Удалить'
        row = self.notes_list_widget.currentRow()  # получаем номер текущего элемента
        if row == -1:  # если ничего не выбрано, то
            return  # выходим из метода

        text = self.notes_list_widget.currentItem().text()

        # выводим на экран сообщение о подтверждении удаления
        msg = QMessageBox()
        msg.addButton('Да', QMessageBox.AcceptRole)
        msg.addButton('Нет', QMessageBox.RejectRole)
        msg.setText('Удалить запись ' + text + '?')

        reply = msg.exec_()  # запускаем сообщение
        if reply == 1:
            return  # если ответ отрицательынй (то есть равен 1), то выходим из метода

        # при положительном ответе мы доходим сюда и удаляем из базы выбранную заметку
        self.db.delete_note(text)

        self.notes_list_widget.takeItem(row)  # удаляем заметку из списка на экране


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
