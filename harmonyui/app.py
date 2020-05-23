import sys
#from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5.QtWidgets import QWidget, QGridLayout, QTableView, QApplication, QPushButton

class MainWindow(QWidget): 

    def __init__(self):
        super(MainWindow, self).__init__()

        self.title = 'Harmony'
        self.left = 10
        self.top = 10
        self.width = 1500
        self.height = 960
        self.initLayout()
        self.initUI()
    
    def initLayout(self):
        self.layout = QGridLayout()

        # tree view | plot        | metadata
        # tree view | plot        | metadata
        # tag       | plot choice | filter

        self.layout.addWidget(QTableView(), 0, 0, 1, 1)
        self.layout.addWidget(QTableView(), 2, 0)

        self.layout.addWidget(QPushButton("Plots!"), 0, 1, 2, 1)
        self.layout.addWidget(QPushButton("Plot Choices"), 2, 1)

        self.layout.addWidget(QPushButton("Meta!"), 0, 2, 2, 1)
        self.layout.addWidget(QPushButton("Filter"), 2, 2)
        
    def initUI(self):
        self.setLayout(self.layout)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()


if __name__ == "__main__": 
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())