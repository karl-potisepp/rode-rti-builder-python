#!/usr/bin/env python

import os
import sys

from PyQt5.QtCore import (QDir, QIODevice, QFile, QFileInfo, Qt, QTextStream, QRect,
        QRectF, QUrl, QPoint)
from PyQt5.QtGui import QDesktopServices, QImage, QImageReader, QPixmap, QPainter, QColor, QPen
from PyQt5.QtWidgets import (QWidget, QAbstractItemView, QApplication, QComboBox,
        QDialog, QFileDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
        QProgressDialog, QPushButton, QSizePolicy, QTableWidget, QGraphicsScene,
        QGraphicsView, QTableWidgetItem, QMessageBox)

class Window(QDialog):

    def __init__(self, parent=None):

        super(Window, self).__init__(parent)

        inputButton = self.createButton("&Select input folder", self.browseForInput)
        inputLabel = QLabel("Input path: ")
        self.inputPath = QLabel(QDir.currentPath())
        self.inputStats = QLabel("")
        self.inputFiles = []
        self.sampleImage = SampleImageWidget(self)

        outputButton = self.createButton("&Select output folder", self.browseForOutput)
        outputLabel = QLabel("Output path:")
        self.outputPath = QLabel(QDir.currentPath())

        startButton = self.createButton("&Start processing", self.process)
        quitButton = self.createButton("&Exit", self.quit)

        mainLayout = QGridLayout()

        mainLayout.addWidget(inputButton, 0, 0)
        mainLayout.addWidget(inputLabel, 0, 1)
        mainLayout.addWidget(self.inputPath, 0, 2)
        mainLayout.addWidget(self.inputStats, 1, 0)
        mainLayout.addWidget(self.sampleImage, 1, 1)

        mainLayout.addWidget(outputButton, 2, 0)
        mainLayout.addWidget(outputLabel, 2, 1)
        mainLayout.addWidget(self.outputPath, 2, 2)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(startButton)
        buttonsLayout.addWidget(quitButton)

        mainLayout.addLayout(buttonsLayout, 3, 0)

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

        #TODO call make_average

        #load and display the first image
        self.sampleImage.setSampleImage(self.inputFiles[0])
        #also display statistics
        self.inputStats.setText(",".join(stats))
        #and show the input directory path to the user
        self.inputPath.setText(directory)

    def browseForOutput(self):
        directory = QFileDialog.getExistingDirectory(self, "Select output folder",
                QDir.currentPath())

        self.outputPath.setText(directory)

    def process(self):

      print "original h & w", self.sampleImage.originalHeight, self.sampleImage.originalWidth
      print "scaled h & w", self.sampleImage.scaledHeight, self.sampleImage.scaledWidth

      scaleCoefficient = self.sampleImage.originalWidth / self.sampleImage.scaledWidth
      ballBBTopLeftX = self.sampleImage.graphicsView.topLeft.x()*scaleCoefficient
      ballBBTopLeftY = self.sampleImage.graphicsView.topLeft.y()*scaleCoefficient
      ballBBWidth = self.sampleImage.graphicsView.rectangle.rect().width()*scaleCoefficient
      ballBBHeight = self.sampleImage.graphicsView.rectangle.rect().height()*scaleCoefficient

      print ballBBTopLeftX, ballBBTopLeftY, ballBBWidth, ballBBHeight

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

    def quit(self):
      self.close()
      #FIXME quick and dirty
      sys.exit(0)

#TODO an extension to QWidget that can:
# * draw a QPixmap which represents a JPG image
# * capture mouse press events and store their locations
# * if two mouse press locations are stored, overlay a selection box
#   using one coordinate as top left, other as bottom right
# * further mouse presses adjust either the top left or bottom right coordinate
#    whichever is closest
# * OPTIONAL: 'zoom' button to only draw the selected part so the ball can be
#   more closely approximated (also 'reset' button to restore original setting)

class SampleGraphicsView(QGraphicsView):

  def __init__(self, parent=None):
    super(SampleGraphicsView, self).__init__(parent)

    self.topLeft = QPoint(0, 0)
    self.bottomRight = QPoint(10, 10)
    self.rectangle = None

  #TODO more userfriendly selection

  def mousePressEvent(self, event):
    #print "mouse press event!", event.x(), event.y()

    tmpPoint = QPoint(event.x(), event.y())

    dist1 = (self.topLeft-tmpPoint).manhattanLength()
    dist2 = (self.bottomRight-tmpPoint).manhattanLength()

    if dist1 < dist2:

      self.topLeft = tmpPoint
    else:
      self.bottomRight = tmpPoint

    self.rectangle = self.redrawSelection()

  def redrawSelection(self):
    if self.rectangle is not None:
      self.scene().removeItem(self.rectangle)
    return self.scene().addRect(QRectF(self.topLeft, self.bottomRight), QPen(QColor("red")))

class SampleImageWidget(QWidget):

  def __init__(self, parent=None):

    super(SampleImageWidget, self).__init__(parent)

    self.graphicsScene = QGraphicsScene(self)
    self.graphicsView = SampleGraphicsView(self.graphicsScene)

  def setSampleImage(self, pathToFile):

    self.graphicsView.hide()

    #clear scene
    self.graphicsScene.clear()

    #load file
    tmpImage = QImage(pathToFile)
    self.originalHeight = tmpImage.height()
    self.originalWidth = tmpImage.width()
    tmpPixmap = QPixmap(1)
    tmpPixmap.convertFromImage(tmpImage.scaledToWidth(300))
    self.scaledHeight = tmpPixmap.height()
    self.scaledWidth = tmpPixmap.width()

    #add to scene and show
    self.graphicsScene.addPixmap(tmpPixmap)
    self.graphicsView.show()

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
