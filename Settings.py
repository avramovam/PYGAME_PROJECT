import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui
from pygame.math import Vector2 as vec

class Main(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.setWindowTitle('Настройки')
        self.setFixedSize(600, 450)
        pal = self.palette()
        pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window,
                     QtGui.QBrush(QtGui.QPixmap("data/bg_set.png")))
        self.setPalette(pal)
        self.label = QLabel('Музыка')
        self.label.setStyleSheet("QLabel { background-color: rgba(180, 180, 180, 160)}")
        layout.addWidget(self.label, 0, 0)

        radiobutton = QRadioButton("Вкл")
        radiobutton.setChecked(True)
        radiobutton.country = "Вкл"
        radiobutton.toggled.connect(self.onClicked)
        radiobutton.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        layout.addWidget(radiobutton, 0, 20)

        radiobutton = QRadioButton("Выкл")
        radiobutton.country = "Выкл"
        radiobutton.toggled.connect(self.onClicked)
        radiobutton.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        layout.addWidget(radiobutton, 0, 40)

        self.b0 = QPushButton(self)
        self.b0.move(20, 100)
        self.b0.resize(30, 30)
        self.b0.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b0.setText('0')
        self.b0.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        # self.AddFB.clicked.connect(self.open_Add)
        self.b0.clicked.connect(self.b0_clicked)

        self.b1 = QPushButton(self)
        self.b1.move(50, 100)
        self.b1.resize(30, 30)
        self.b1.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b1.setText('10')
        self.b1.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b1.clicked.connect(self.b1_clicked)

        self.b2 = QPushButton(self)
        self.b2.move(80, 100)
        self.b2.resize(30, 30)
        self.b2.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b2.setText('20')
        self.b2.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b2.clicked.connect(self.b2_clicked)

        self.b3 = QPushButton(self)
        self.b3.move(110, 100)
        self.b3.resize(30, 30)
        self.b3.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b3.setText('30')
        self.b3.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b3.clicked.connect(self.b3_clicked)

        self.b4 = QPushButton(self)
        self.b4.move(140, 100)
        self.b4.resize(30, 30)
        self.b4.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b4.setText('40')
        self.b4.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b4.clicked.connect(self.b4_clicked)

        self.b5 = QPushButton(self)
        self.b5.move(170, 100)
        self.b5.resize(30, 30)
        self.b5.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b5.setText('50')
        self.b5.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b5.clicked.connect(self.b5_clicked)

        self.b6 = QPushButton(self)
        self.b6.move(200, 100)
        self.b6.resize(30, 30)
        self.b6.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b6.setText('60')
        self.b6.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b6.clicked.connect(self.b6_clicked)

        self.b7 = QPushButton(self)
        self.b7.move(230, 100)
        self.b7.resize(30, 30)
        self.b7.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b7.setText('70')
        self.b7.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b7.clicked.connect(self.b7_clicked)

        self.b8 = QPushButton(self)
        self.b8.move(260, 100)
        self.b8.resize(30, 30)
        self.b8.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b8.setText('80')
        self.b8.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b8.clicked.connect(self.b8_clicked)

        self.b9 = QPushButton(self)
        self.b9.move(290, 100)
        self.b9.resize(30, 30)
        self.b9.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b9.setText('90')
        self.b9.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b9.clicked.connect(self.b9_clicked)

        self.b10 = QPushButton(self)
        self.b10.move(320, 100)
        self.b10.resize(30, 30)
        self.b10.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.b10.setText('100')
        self.b10.setFont(QtGui.QFont('', 12, QtGui.QFont.Bold))
        self.b10.clicked.connect(self.b10_clicked)

    def onClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            print("музыка %s" % (radioButton.country))
            # Запись в файл
            if radioButton.country == "Выкл":
                with open('sound_on.txt', 'w') as f:
                    f.write("0")
            elif radioButton.country == "Вкл":
                with open('sound_on.txt', 'w') as f:
                    f.write("1")


    # функция сброса вида кнопок

    def clear_bs(self):
        self.b0.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b1.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b2.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b3.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b4.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b5.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b6.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b7.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b8.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b9.setStyleSheet("background-color: rgba(180, 180, 180, 160)")
        self.b10.setStyleSheet("background-color: rgba(180, 180, 180, 160)")

    # Функция записи громкости
    def write_volume(self, n):
        with open('music_volume.txt', 'w') as f:
            f.write(str(n))

    # блок обработки "ползунка"

    def b0_clicked(self):
        self.clear_bs()
        self.b0.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(0)

    def b1_clicked(self):
        self.clear_bs()
        self.b1.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(10)

    def b2_clicked(self):
        self.clear_bs()
        self.b2.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(20)

    def b3_clicked(self):
        self.clear_bs()
        self.b3.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(30)

    def b4_clicked(self):
        self.clear_bs()
        self.b4.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(40)

    def b5_clicked(self):
        self.clear_bs()
        self.b5.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(50)

    def b6_clicked(self):
        self.clear_bs()
        self.b6.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(60)

    def b7_clicked(self):
        self.clear_bs()
        self.b7.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(70)

    def b8_clicked(self):
        self.clear_bs()
        self.b8.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(80)

    def b9_clicked(self):
        self.clear_bs()
        self.b9.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(90)

    def b10_clicked(self):
        self.clear_bs()
        self.b10.setStyleSheet("background-color: rgba(180, 180, 180, 255)")
        self.write_volume(100)


if __name__ == '__main__':
    # Подстраховка от пустого файла
    with open('sound_on.txt', 'w') as f:
        f.write("0")

    app = QApplication(sys.argv)
    wnd = Main()
    wnd.show()
    sys.exit(app.exec())