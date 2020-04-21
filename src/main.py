from PySide2 import QtWidgets
from PySide2.QtWidgets import QFileDialog
from alpha_alg import AlphaAlgorithm
from heuristic_miner import HeuristicMiner

class Algorithm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Algorithm, self).__init__(parent)

        self.logsPath = ""

        self.logsBtn = QtWidgets.QPushButton()
        self.logsBtn.setText("Wybierz logi")
        self.logsBtn.clicked.connect(self.selectLogs)

        outputLabel = QtWidgets.QLabel("Podaj nazwe pliku do zapisu grafu:")
        self.outputLE = QtWidgets.QLineEdit()

        algChooseLabel = QtWidgets.QLabel("Wybierz algorytm:")
        self.algComboBox = QtWidgets.QComboBox()
        self.algComboBox.addItems(["", "alpha", "heuristic_miner"])
        self.algComboBox.activated.connect(self.checkAlg)

        self.runBtn = QtWidgets.QPushButton()
        self.runBtn.setText("Uruchom")
        self.runBtn.clicked.connect(self.checkAndRun)

        self.heuristicThreshold1Label = QtWidgets.QLabel("thresh_direct_followers")
        self.heuristicThreshold1 = QtWidgets.QLineEdit()
        self.heuristicThreshold1.setText("0.9")

        self.heuristicThreshold2Label = QtWidgets.QLabel("thresh_parallel")
        self.heuristicThreshold2 = QtWidgets.QLineEdit()
        self.heuristicThreshold2.setText("0.7")

        self.heuristicThreshold3Label = QtWidgets.QLabel("thresh_oneloop")
        self.heuristicThreshold3 = QtWidgets.QLineEdit()
        self.heuristicThreshold3.setText("0.9")

        self.heuristicThreshold4Label = QtWidgets.QLabel("thresh_twoloop")
        self.heuristicThreshold4 = QtWidgets.QLineEdit()
        self.heuristicThreshold4.setText("0.9")

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.logsBtn, 0, 0)
        mainLayout.addWidget(outputLabel, 1, 0)
        mainLayout.addWidget(self.outputLE, 1, 1)
        mainLayout.addWidget(algChooseLabel, 2, 0)
        mainLayout.addWidget(self.algComboBox, 2, 1)
        mainLayout.addWidget(self.heuristicThreshold1Label, 3, 0)
        mainLayout.addWidget(self.heuristicThreshold1, 3, 1)
        mainLayout.addWidget(self.heuristicThreshold2Label, 4, 0)
        mainLayout.addWidget(self.heuristicThreshold2, 4, 1)
        mainLayout.addWidget(self.heuristicThreshold3Label, 5, 0)
        mainLayout.addWidget(self.heuristicThreshold3, 5, 1)
        mainLayout.addWidget(self.heuristicThreshold4Label, 6, 0)
        mainLayout.addWidget(self.heuristicThreshold4, 6, 1)
        mainLayout.addWidget(self.runBtn, 7, 0)

        self.setLayout(mainLayout)
        self.setWindowTitle("Algorytm")
        self.hideThresholds()

    def selectLogs(self):
        dialog = QFileDialog()
        self.logsPath = dialog.getOpenFileName()

    def showThresholds(self):
        self.heuristicThreshold1Label.show()
        self.heuristicThreshold2Label.show()
        self.heuristicThreshold3Label.show()
        self.heuristicThreshold4Label.show()
        self.heuristicThreshold1.show()
        self.heuristicThreshold2.show()
        self.heuristicThreshold3.show()
        self.heuristicThreshold4.show()

    def hideThresholds(self):
        self.heuristicThreshold1Label.hide()
        self.heuristicThreshold2Label.hide()
        self.heuristicThreshold3Label.hide()
        self.heuristicThreshold4Label.hide()
        self.heuristicThreshold1.hide()
        self.heuristicThreshold2.hide()
        self.heuristicThreshold3.hide()
        self.heuristicThreshold4.hide()

    def checkAlg(self):
        if self.algComboBox.currentText() == "heuristic_miner":
            self.showThresholds()
        else:
            self.hideThresholds()

    def checkAndRun(self):
        if self.logsPath != "" and self.outputLE.text() != "":
            if self.algComboBox.currentText() == "alpha":
                alpha = AlphaAlgorithm()
                alpha.read_log_file(self.logsPath[0])
                alpha.build_model()
                alpha.create_graph(self.outputLE.text())
            elif self.algComboBox.currentText() == "heuristic_miner":
                hminer = HeuristicMiner(float(self.heuristicThreshold1.text()),
                                        float(self.heuristicThreshold2.text()),
                                        float(self.heuristicThreshold3.text()),
                                        float(self.heuristicThreshold4.text()))
                hminer.read_log_file(self.logsPath[0])
                hminer.build_model()
                hminer.create_graph(self.outputLE.text())
            else:
                dialog = QtWidgets.QMessageBox()
                dialog.setText("Wybierz algorytm")
                dialog.exec_()
        else:
            dialog = QtWidgets.QMessageBox()
            dialog.setText("Wybierz scieżki logów i nazwe outputu")
            dialog.exec_()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    algorithm = Algorithm()
    algorithm.show()

    sys.exit(app.exec_())
