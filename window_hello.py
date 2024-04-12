import sys
import random
from datetime import datetime

from PIL import Image
from cryptography.fernet import Fernet
from PyQt5 import uic
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog

import utils
import window_main


class WindowHello(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('hello.ui', self)
        self.initUI()

    def initUI(self):
        self.newBtn.clicked.connect(self.new)
        self.loadBtn.clicked.connect(self.load)

    def new(self):
        f, _ = QFileDialog.getOpenFileName(
            self,
            'Выбрать картинку', '',
            f"Картинки ({' '.join([f'*.{i.data().decode()}' for i in QImageReader.supportedImageFormats()])})")

        if not f:
            return
        print(f)

        name, ok_pressed = QInputDialog.getText(self, 'Введите имя', 'Как вас называть')
        if not ok_pressed:
            return
        login = str(random.randint(1, 10000)).rjust(4, '0')
        cur = utils.base.cursor()
        while cur.execute(f"select * from users where id={login}").fetchone():
            login = str(random.randint(1, 10000)).rjust(4, '0')
        key = Fernet.generate_key()
        cur.execute(f"""insert into users(id, name, lastsave, lastseen)
        values({login}, '{name}', 'никогда', '{str(datetime.now())}')""")
        utils.base.commit()
        data = utils.seq_to_bin(login.encode() + key)
        data_size = len(data)  # 384

        im = Image.open(f).convert('RGB')
        pxs = tuple(im.getdata())
        out = []
        for i in range(0, data_size, 3):
            out.append(utils.encode_pixel(pxs[i], data[i:i + 3]))
            print(end='')
        # for px in pxs[data_size::3]:
        #     out.append(utils.encode_pixel(px, '{0:03b}'.format(random.randint(0, 1000)).encode()))
        im.putdata(out)
        im.save(f'{f[:-4]}_key.png')

        self.window_main = window_main.WindowMain(login, key, f)
        self.window_main.show()
        self.close()

    def load(self):
        f, _ = QFileDialog.getOpenFileName(
            self,
            'Выбрать ключ-картинку', '',
            f"Картинки (*.png)")

        if not f:
            return
        print(f)

        im = Image.open(f).convert('RGB')
        pxs = tuple(im.getdata())
        binary = []
        for px in pxs[:384]:
            batch = utils.decode_pixel(px)
            for i in range(3):
                binary.append(batch[i])
            print(end='')
        out = utils.bin_to_str(binary)

        self.window_main = window_main.WindowMain(out[:4], out[4:].encode(), f)
        self.window_main.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WindowHello()
    ex.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    sys.exit(app.exec_())
