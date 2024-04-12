import datetime
import sys

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFrame, QVBoxLayout, QPlainTextEdit, \
    QCommandLinkButton, QLineEdit, QMessageBox
from cryptography import fernet
from cryptography.fernet import Fernet

import main_ui
import utils
import window_hello


class WindowMain(QMainWindow, main_ui.Ui_Main):
    def __init__(self, login: str, key: bytes, path: str):
        super().__init__()
        self.setupUi()
        cur = utils.base.cursor()
        self.name = cur.execute(f"select name from users where id={login}").fetchone()[0]
        self.usrName.setText('Привет, ' + self.name)
        self.login = login
        self.key = key
        self.img_path = path
        self.last_seen = cur.execute(f"select lastseen from users where id={login}").fetchone()[0]
        cur.execute(f"update users set lastseen='{str(datetime.datetime.now())}' where id={self.login}")
        utils.base.commit()
        self.initUI()
        last_save = cur.execute(f"select lastsave from users where id={login}").fetchone()[0]
        self.lastSave.setText('Последнее сохранение: ' + last_save)
        for row in cur.execute(f"select * from notes where author={self.login}").fetchall():
            note = Note(self, identifier=row[0])
            note.titleEdit.setText(row[2])
            note.textEdit.setPlainText(row[3])
            self.vertLay.addWidget(note)
            note.show()

    def newImageDialog(self, e):
        self.img_dialog = ImageDialog(self.img_path)
        self.img_dialog.show()

    def initUI(self):
        self.outBtn.clicked.connect(self.back)
        self.newBtn.clicked.connect(self.new)
        self.aboutBtn.clicked.connect(
            lambda: QMessageBox.about(self, 'О программе',
                                      'EncryptedNotes v1.0\nСделал Марк Каргин'))
        self.saveIcon.mousePressEvent = self.newImageDialog
        self.lastSave.mousePressEvent = \
            lambda e: QMessageBox.about(self, 'Сведения об аккаунте', f'''id: {self.login}
Имя: {self.name}
Последний вход: {self.last_seen}
{self.lastSave.text()}
            ''')

    def new(self):
        note = Note(self, new=True)
        self.vertLay.addWidget(note)
        note.show()

    def back(self):
        self.window_hello = window_hello.WindowHello()
        self.window_hello.show()
        self.close()


class ImageDialog(QMainWindow):
    def __init__(self, path: str):
        super().__init__()
        uic.loadUi('image.ui', self)
        self.setWindowTitle('Картинка-ключ')
        self.imgLabel.setPixmap(QPixmap(path))


class Note(QWidget):
    def __init__(self, parent, new=False, identifier=None):
        super().__init__()
        uic.loadUi('note.ui')
        self.login = parent.login
        self.key = parent.key
        self.container = parent
        self.id = identifier
        self.decrypted = new
        self.initUI(self)
        self.readBtn.clicked.connect(self.read)
        self.del_Btn.clicked.connect(self.delete)

    def initUI(self, Form):
        self.gridLayout_3 = QGridLayout(Form)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.noteFrame = QFrame(Form)
        self.noteFrame.setObjectName(u"noteFrame")
        self.noteFrame.setStyleSheet(u"QFrame {\n"
                                     "	background-color: rgb(48, 50, 72);\n"
                                     "	border-radius: 10px\n"
                                     "}")
        self.gridLayout_4 = QGridLayout(self.noteFrame)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.textEdit = QPlainTextEdit(self.noteFrame)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setStyleSheet(u"QPlainTextEdit {\n"
                                    "	background-color: rgb(255, 255, 255);\n"
                                    "	border-radius: 5px;\n"
                                    "	font: 11pt \"MS Shell Dlg 2\";\n"
                                    "}")
        self.textEdit.setPlaceholderText("Введите текст...")
        self.verticalLayout_6.addWidget(self.textEdit)
        self.gridLayout_4.addLayout(self.verticalLayout_6, 1, 0, 1, 1)
        self.titleEdit = QLineEdit(self.noteFrame)
        self.titleEdit.setObjectName(u"titleEdit")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.titleEdit.setFont(font)
        self.titleEdit.setStyleSheet(u"QLineEdit {\n"
                                     "	border-radius: 4px\n"
                                     "}")
        self.titleEdit.setPlaceholderText(u"\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a")
        self.gridLayout_4.addWidget(self.titleEdit, 0, 0, 1, 1)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.readBtn = QCommandLinkButton(self.noteFrame)
        self.readBtn.setObjectName(u"readBtn")
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setWeight(75)
        self.readBtn.setFont(font1)
        self.readBtn.setStyleSheet(u"QPushButton {\n"
                                   "	background-color: rgb(255, 255, 255);\n"
                                   "	border: 2px solid rgb(54, 66, 182);\n"
                                   "	color: rgb(54, 66, 182);\n"
                                   "	border-radius: 6px\n"
                                   "}\n"
                                   "QPushButton:hover {\n"
                                   "	background-color: rgb(190, 190, 255);\n"
                                   "}\n"
                                   "QPushButton:pressed {\n"
                                   "	background-color: rgb(150, 150, 255);\n"
                                   "}")
        icon = QIcon()
        iconThemeName = u"."
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        self.readBtn.setIcon(icon)
        self.verticalLayout_7.addWidget(self.readBtn)
        self.del_Btn = QCommandLinkButton(self.noteFrame)
        self.del_Btn.setObjectName(u"del_Btn")
        self.del_Btn.setFont(font1)
        self.del_Btn.setStyleSheet(u"QPushButton {\n"
                                   "	color: rgb(255, 255, 255);\n"
                                   "	background-color: rgb(255, 69, 72);\n"
                                   "	border-radius: 6px\n"
                                   "}\n"
                                   "QPushButton:hover {\n"
                                   "	background-color: rgb(200, 54, 57);\n"
                                   "}\n"
                                   "QPushButton:pressed {\n"
                                   "	background-color: rgb(150, 41, 44);\n"
                                   "}")
        self.del_Btn.setIcon(icon)
        self.verticalLayout_7.addWidget(self.del_Btn)
        self.gridLayout_4.addLayout(self.verticalLayout_7, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.noteFrame, 0, 1, 1, 1)
        self.retranslateUi()

    def retranslateUi(self):
        self.readBtn.setText("Сохранить" if self.decrypted else "Прочесть")
        self.del_Btn.setText("Удалить")

    def read(self):
        if self.decrypted:
            cur = utils.base.cursor()
            time = str(datetime.datetime.now())

            if self.id is None:
                cur.execute(f"""insert into notes(author, title, content)
values({self.login},'{self.titleEdit.text()}', '{Fernet(self.key).encrypt(
                self.textEdit.toPlainText().encode()).decode()}')""")
                self.id = cur.execute('SELECT id FROM notes ORDER BY id DESC LIMIT 1').fetchone()[0]
            else:
                cur.execute(f"""update notes set author={self.login} where id={self.id}""")
                cur.execute(f"""update notes set title='{self.titleEdit.text()}' where id={self.id}""")
                cur.execute(f"""update notes set  content='{Fernet(self.key).encrypt(
                    self.textEdit.toPlainText().encode()).decode()}' where id={self.id}""")
            cur.execute(f"update users set lastsave='{time}' where id={self.login}")

            self.container.lastSave.setText('Последнее сохранение: ' + time)

            utils.base.commit()
        else:
            self.readBtn.setText('Сохранить')
            try:
                self.textEdit.setPlainText(Fernet(self.key).decrypt(self.textEdit.toPlainText().encode()).decode())
            except fernet.InvalidToken:
                QMessageBox.about(self, 'Ошибка', 'Неверный ключ')
                return
            self.decrypted = True

    def delete(self):
        self.container.vertLay.removeWidget(self)
        utils.base.cursor().execute(f"delete from notes where author={self.login}")
        utils.base.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WindowMain('0000', Fernet.generate_key())
    ex.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    sys.exit(app.exec_())
