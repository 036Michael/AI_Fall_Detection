from PyQt5 import QtWidgets, QtCore
import sys

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle('跌倒偵測系統')
        self.resize(1920,1080)
        self.ui()

    def button_clicked(self):
        print('Button clicked!')
        self.shows()

    def shows(self):
        print("show")
        
    def ui(self):
        pushButton = QtWidgets.QPushButton(self)    
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        pushButton.setGeometry(QtCore.QRect(100, 70, 113, 32))
        pushButton.setObjectName("pushButton")
        pushButton.setText("PushButton")
        pushButton.clicked.connect(self.button_clicked)

    def closeEvent(self, event):
        print("close")
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWidget()
    MainWindow.show()
    sys.exit(app.exec_())



