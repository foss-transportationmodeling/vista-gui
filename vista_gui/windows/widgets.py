# -*- coding: utf-8 -*-
import re

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.phonon import Phonon
from misc.errors import *


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def check(self, text):
        text = self.text()
        try:
            if len(text) == 0:
                raise TextError("Enter a non-empty string")
            if not re.match("[A-Za-z]", text[0]):
                text = text[1:]
                raise TextError("First character has to be a alphabet")

            for i in text[1:]:
                if not re.match("[A-Za-z_0-9]", i):
                    text.replace(i, '')
                    raise TextError("""Name can only comprise """
                                    """of alphabets and an underscore (_)""")
        except TextError, e:
            QMessageBox.information(self, "Warning",
                                    "%s" % e,
                                    QMessageBox.Ok)
            self.setText(text)
            self.selectAll()
            self.setFocus()
        return True


class ComboBoxFolder(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxFolder, self).__init__(parent)

    def browse_folder(self, index):
        if index == self.count()-1:
            location = (QFileDialog.getExistingDirectory(
                        self, "Project Location",
                        "C:\workspace\\vista\project\ctdot_test",
                        QFileDialog.ShowDirsOnly)
                        )
            if len(location) > 0:
                indexOfFolder = self.is_present(location)
                if indexOfFolder is None:
                    self.insertItem(0, location)
                    self.setCurrentIndex(0)
                else:
                    self.setCurrentIndex(indexOfFolder)
            else:
                self.setCurrentIndex(0)

    def is_present(self, location):
        for i in range(self.count()):
            if location == self.itemText(i):
                return i
        return None


class ComboBoxFile(QComboBox):
    def __init__(self, parent=None):
        super(ComboBoxFile, self).__init__(parent)

    def browse_file(self, index):
        if index == self.count()-1:
            # TODO: Change the video file types based on what codecs are
            # supported
            fileName = (QFileDialog.getOpenFileName(
                    self, "Browse to select file",
                    "C:\workspace\\vista\project\ctdot_test",
                    "Video Files (*.mp4 *.avi)")
                    )
            if not fileName.isEmpty():
                indexOfFile = self.is_present(fileName)
                if indexOfFile is None:
                    self.insertItem(1, fileName)
                    self.setCurrentIndex(1)
                else:
                    self.setCurrentIndex(indexOfFile)
            else:
                self.setCurrentIndex(0)

    def is_present(self, file):
        for i in range(self.count()):
            if file == self.itemText(i):
                return i
        return None

    def find_and_set(self, text):
        for i in range(self.count()):
            if self.itemText(i) == ('%s' % text):
                self.setCurrentIndex(i)
                return True
        else:
            return False


class ListWidget(QListWidget):
    def __init__(self, parent=None, extendedSelection=False):
        super(ListWidget, self).__init__(parent)
        if extendedSelection is True:
            self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def remove(self):
        self.takeItem(self.currentRow())

    def remove_items(self, items):
        for i in items:
            row = self.row(i)
            self.takeItem(row)

    def add_text_list(self, textList):
        self.clear()
        for i in textList:
            self.addItem(i)
        self.sortItems()


class ComboBox(QComboBox):
    """
    This is a reimplementation of the QComboBox so that
    1) the strings of the keys are added as items and
    2) for the selected item, a function returning the value corresponding
    to the text is implemented.
    """
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.currentIndexChanged.connect(self.print_value)

    def add_items(self, itemsValDict):
        if not isinstance(itemsValDict, dict):
            raise InputError("Dictionary object expected for addItems {0}"
                             .format(type(itemsValDict)))
        else:
            self.itemsValDict = itemsValDict
            itemsText = self.itemsValDict.keys()
            itemsText.sort()
            self.addItems(itemsText)

    def current_item_value(self):
        text = self.currentText()
        val = self.itemsValDict[text]
        return val

    def print_value(self):
        value = self.current_item_value()
        # print ("the select value is: {0} and type is {1}"
        #       .format(value, type(value)))


class OpenProject(QFileDialog):
    def __init__(self, parent=None):
        super(OpenProject, self).__init__(parent)
        self.file = (self.getOpenFileName(
                     parent, "Browse to select file",
                     "C:\workspace\\vista\project\ctdot_test",
                     "VISTA File (*.vista)"))


class TableView(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        from PySide.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery

        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("C:\\workspace\\vista\\project\\ctdot_test\\car_count_db")
        db.open()

        projectModel = QSqlQueryModel()
        projectModel.setQuery("select * from CarTable_exp5", db)

        projectView = QTableView()
        projectView.setModel(projectModel)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel |
                                           QDialogButtonBox.Ok)

        layout = QVBoxLayout(self)
        layout.addWidget(projectView)
        layout.addWidget(dialogButtonBox)
        self.setLayout(layout)


class TWidget(QWidget):

    def __init__(self, parent=None):
        super(TWidget, self).__init__(parent=parent)
        self.r = 200
        self.g = 10
        self.b = 50

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def mousePressEvent(self, QMouseEvent):
        print QMouseEvent.pos()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        qp.setBrush(QColor(self.r, self.g, self.b))
        qp.drawRect(0, 0, size.width(), size.height())


class VWidget(Phonon.VideoWidget):

    def __init__(self, parent=None):
        super(VWidget, self).__init__(parent=parent)
        self.poly = []
        self.initPoly()
        self.unload()
        self.initRegions()
        self.polydraw = False
        self.loadpresets()
        # self.video.size().toTuple()

    def initRegions(self):
        self.start = []
        self.end = []
        self.left = []
        self.right = []
        self.regions = {
            'start': self.start,
            'end': self.end,
            'right': self.right,
            'left': self.left}
        self.clicks = {
            'start': 0,
            'end': 0,
            'right': 0,
            'left': 0}

    def initPoly(self):
        for i in range(50):
            self.poly.append(TWidget(parent=self))

    def mousePressEvent(self, QMouseEvent):
        xy = QMouseEvent.pos()
        self.draw(xy.x(), xy.y())

    def draw(self, x, y):
        if self.polydraw:
            width = self.size().toTuple()[0]
            height = self.size().toTuple()[1]
            size = 10
            tol = 20
            if x < tol:
                x = -10
                size = 20
            if y < tol:
                y = -10
                size = 20
            if x > width - tol:
                x = width - 10
                size = 20
            if y > height - tol:
                y = height - 10
                size = 20
            self.regions[self.region][self.clicks[self.region]] = [
                x, y, size, size]
            self.polyGeom(self.regions[self.region][self.clicks[self.region]],
                          self.clicks[self.region])
            self.clicks[self.region] += 1
            if self.clicks[self.region] > len(self.poly) - 1:
                self.clicks[self.region] = 0

    def polyGeom(self, first, i):
        self.poly[i].setGeometry(first[0], first[1], first[2], first[3])

    def load(self, region):
        self.region = region
        self.polyDraw = False
        for i in range(50):
            self.polyGeom(self.regions[self.region][i], i)

    def loadpresets(self):
        for i in range(50):
            self.start.append([0, 0, 0, 0])
            self.end.append([0, 0, 0, 0])
            self.left.append([0, 0, 0, 0])
            self.right.append([0, 0, 0, 0])

    def clear(self):
        for i in range(50):
            self.poly[i].setGeometry(0, 0, 0, 0)
            self.regions[self.region][i] = [0, 0, 0, 0]
        self.clicks[self.region] = 0

    def clearLast(self):
        self.clicks[self.region] = (
            0 if self.clicks[self.region] < 1 else self.clicks[self.region] - 1
            )
        self.poly[self.clicks[self.region]].setGeometry(0, 0, 0, 0)
        self.regions[self.region][self.clicks[self.region]] = [0, 0, 0, 0]

    def unload(self):
        for i in range(50):
            self.poly[i].setGeometry(0, 0, 0, 0)

    def getDots(self, region):
        return self.regions[region]

    def clearAll(self):
        for i in self.regions.values():
            for j in range(50):
                i[j] = [0, 0, 0, 0]
        for i in self.clicks:
            self.clicks[i] = 0
        self.unload()

    def loadCustom(self, points, region):
        self.region = region
        self.clear()
        for i in points:
            self.regions[self.region][self.clicks[self.region]] = i
            self.clicks[self.region] += 1


if __name__ == '__main__':
    import sys
    import pandas as pd
    import numpy as np
    app = QApplication(sys.argv)
    videosDf = pd.read_csv("videoDf.csv", header=0)

    window = VDetectParamsWidget(videosDf)
    window.show()
    sys.exit(app.exec_())
