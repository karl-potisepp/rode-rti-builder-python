#!/usr/bin/env python

import os

from PyQt5.QtCore import (QDir, QIODevice, QFile, QFileInfo, Qt, QTextStream,
        QUrl)
from PyQt5.QtGui import QDesktopServices, QImage, QImageReader, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
        QDialog, QFileDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
        QProgressDialog, QPushButton, QSizePolicy, QTableWidget,
        QTableWidgetItem, QMessageBox)

#TODO an extension to QWidget that can:
# * draw a QPixmap which represents a JPG image
# * capture mouse press events and store their locations
# * if two mouse press locations are stored, overlay a selection box
#   using one coordinate as top left, other as bottom right
# * further mouse presses adjust either the top left or bottom right coordinate
#    whichever is closest
# * OPTIONAL: 'zoom' button to only draw the selected part so the ball can be
#   more closely approximated (also 'reset' button to restore original setting)

class Window(QDialog):

    def __init__(self, parent=None):

        super(Window, self).__init__(parent)

        inputButton = self.createButton("&Select input folder", self.browseForInput)
        inputLabel = QLabel("Input path: ")
        self.inputPath = QLabel(QDir.currentPath())
        self.inputStats = QLabel("")
        self.inputFiles = []
        #self.exampleImage = QPixMap()
        self.exampleImageDisplay = QLabel()

        outputButton = self.createButton("&Select output folder", self.browseForOutput)
        outputLabel = QLabel("Output path:")
        self.outputPath = QLabel(QDir.currentPath())

        startButton = self.createButton("&Start processing", self.process)
        quitButton = self.createButton("&Exit", self.close)

        #self.fileComboBox = self.createComboBox("*")
        #self.textComboBox = self.createComboBox()
        #self.directoryComboBox = self.createComboBox(QDir.currentPath())

        #fileLabel = QLabel("Named:")
        #textLabel = QLabel("Containing text:")
        #directoryLabel = QLabel("In directory:")
        #self.filesFoundLabel = QLabel()

        #self.createFilesTable()



        mainLayout = QGridLayout()
        #mainLayout.addWidget(fileLabel, 0, 0)
        #mainLayout.addWidget(self.fileComboBox, 0, 1, 1, 2)
        #mainLayout.addWidget(textLabel, 1, 0)
        #mainLayout.addWidget(self.textComboBox, 1, 1, 1, 2)
        #mainLayout.addWidget(directoryLabel, 2, 0)
        #mainLayout.addWidget(self.directoryComboBox, 2, 1)

        mainLayout.addWidget(inputButton, 0, 0)
        mainLayout.addWidget(inputLabel, 0, 1)
        mainLayout.addWidget(self.inputPath, 0, 2)
        mainLayout.addWidget(self.inputStats, 1, 0)
        mainLayout.addWidget(self.exampleImageDisplay, 1, 1)

        mainLayout.addWidget(outputButton, 2, 0)
        mainLayout.addWidget(outputLabel, 2, 1)
        mainLayout.addWidget(self.outputPath, 2, 2)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(startButton)
        buttonsLayout.addWidget(quitButton)

        mainLayout.addLayout(buttonsLayout, 3, 0)

        #mainLayout.addWidget(self.filesTable, 3, 0, 1, 3)
        #mainLayout.addWidget(self.filesFoundLabel, 4, 0)
        #mainLayout.addLayout(buttonsLayout, 5, 0, 1, 3)
        self.setLayout(mainLayout)

        self.setWindowTitle("Find Files")
        self.resize(700, 300)

    def createButton(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button

    def browseForInput(self):
        directory = QFileDialog.getExistingDirectory(self, "Select input folder",
                QDir.currentPath())

        #count the number of JPG and TIFF files
        countsPerExtension = {}
        for root, dirs, files in os.walk(directory):
          for f in files:

            #TODO more per-file auditing here?

            if f.lower().endswith("jpg") or f.lower().endswith("jpeg"):
              if "JPG" not in countsPerExtension:
                countsPerExtension["JPG"] = 0
              countsPerExtension["JPG"] += 1
              self.inputFiles.append(os.path.join(root, f))
            elif f.lower().endswith("tiff"):
              if "TIFF" not in countsPerExtension:
                countsPerExtension["TIFF"] = 0
              countsPerExtension["TIFF"] += 1
              self.inputFiles.append(os.path.join(root, f))
          #do not descend recursively
          break

        stats = []
        for extension in countsPerExtension:
          stats.append(extension + ": " + str(countsPerExtension[extension]) + " files")

        #load and display the first image
        self.exampleImage = QImage()
        if self.exampleImage.load(self.inputFiles[0]):
          print "load success"
          tmpPixmap = QPixmap(1)
          tmpPixmap.convertFromImage(self.exampleImage.scaledToWidth(300))
          self.exampleImageDisplay.setPixmap(tmpPixmap)

        self.inputStats.setText(",".join(stats))
        self.inputPath.setText(directory)

    def browseForOutput(self):
        directory = QFileDialog.getExistingDirectory(self, "Select output folder",
                QDir.currentPath())

        self.outputPath.setText(directory)

    def process(self):

        QMessageBox.information(self, "Processing",
          "Processing files in " + self.inputPath.text())

        print "executing find-ball3.ws on ", '''
        nip2 -bp find-ball3.ws
          --set Workspaces.tab2.G1='Image_file "gertrud_closeup-avg.jpg"'
          --set Workspaces.tab2.G17=2200
          --set Workspaces.tab2.G18=1600
          --set Workspaces.tab2.G19=500
          --set Workspaces.tab2.G20=500
          --set main=[Workspaces.tab2.F2,Workspaces.tab2.F5]
          '''

        QMessageBox.information(self, "Done",
          "Output written to" + self.outputPath.text())

    #FIXME the following is leftovers from example code, can be useful,
    #but currently not needed
'''
    @staticmethod
    def updateComboBox(comboBox):
        if comboBox.findText(comboBox.currentText()) == -1:
            comboBox.addItem(comboBox.currentText())



    def findFiles(self, files, text):
        progressDialog = QProgressDialog(self)

        progressDialog.setCancelButtonText("&Cancel")
        progressDialog.setRange(0, files.count())
        progressDialog.setWindowTitle("Find Files")

        foundFiles = []

        for i in range(files.count()):
            progressDialog.setValue(i)
            progressDialog.setLabelText("Searching file number %d of %d..." % (i, files.count()))
            QApplication.processEvents()

            if progressDialog.wasCanceled():
                break

            inFile = QFile(self.currentDir.absoluteFilePath(files[i]))

            if inFile.open(QIODevice.ReadOnly):
                stream = QTextStream(inFile)
                while not stream.atEnd():
                    if progressDialog.wasCanceled():
                        break
                    line = stream.readLine()
                    if text in line:
                        foundFiles.append(files[i])
                        break

        progressDialog.close()

        return foundFiles

    def showFiles(self, files):
        for fn in files:
            file = QFile(self.currentDir.absoluteFilePath(fn))
            size = QFileInfo(file).size()

            fileNameItem = QTableWidgetItem(fn)
            fileNameItem.setFlags(fileNameItem.flags() ^ Qt.ItemIsEditable)
            sizeItem = QTableWidgetItem("%d KB" % (int((size + 1023) / 1024)))
            sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            sizeItem.setFlags(sizeItem.flags() ^ Qt.ItemIsEditable)

            row = self.filesTable.rowCount()
            self.filesTable.insertRow(row)
            self.filesTable.setItem(row, 0, fileNameItem)
            self.filesTable.setItem(row, 1, sizeItem)

        self.filesFoundLabel.setText("%d file(s) found (Double click on a file to open it)" % len(files))



    def createComboBox(self, text=""):
        comboBox = QComboBox()
        comboBox.setEditable(True)
        comboBox.addItem(text)
        comboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return comboBox

    def createFilesTable(self):
        self.filesTable = QTableWidget(0, 2)
        self.filesTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.filesTable.setHorizontalHeaderLabels(("File Name", "Size"))
        self.filesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.filesTable.verticalHeader().hide()
        self.filesTable.setShowGrid(False)

        self.filesTable.cellActivated.connect(self.openFileOfItem)

    def openFileOfItem(self, row, column):
        item = self.filesTable.item(row, 0)

        QMessageBox.information(self, "Success!",
        "Hello \"%s\"!" % item.text())

        QDesktopServices.openUrl(QUrl(self.currentDir.absoluteFilePath(item.text())))

    #FIXME
'''

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
