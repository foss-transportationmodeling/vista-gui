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

class ProjectOptionsDialog(QDialog):
    """
    In this widget the project properties will
    be collected.
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.setFixedSize(QSize(800, 400))

        nameLabel = QLabel("a. Enter project name")
        self.nameLineEdit = LineEdit()
        self.nameLineEdit.setText("Project_Name")
        self.nameLineEdit.selectAll()
        nameLabel.setBuddy(self.nameLineEdit)

        locationLabel = QLabel("b. Select a project file location")
        self.locationComboBox = ComboBoxFolder()
        (self.locationComboBox.addItems(
         ["C:\workspace\\vista\project\ctdot_test",
          "Browse to select folder..."]))
        locationLabel.setBuddy(self.locationComboBox)

        descLabel = QLabel("c. Enter project description (Optional)")
        self.descTextEdit = QTextEdit()
        descLabel.setBuddy(self.descTextEdit)

        videoLabel = QLabel("d. Select traffic video(s) for this project")
        selectButton = QPushButton("Select")
        clearSelectedButton = QPushButton("Clear")
        self.videoFileListWidget = ListWidget(extendedSelection=True)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel |
                                           QDialogButtonBox.Ok)

        projectVLayout = QVBoxLayout()
        projectVLayout.addWidget(nameLabel)
        projectVLayout.addWidget(self.nameLineEdit)
        projectVLayout.addWidget(locationLabel)
        projectVLayout.addWidget(self.locationComboBox)
        projectVLayout.addWidget(descLabel)
        projectVLayout.addWidget(self.descTextEdit)

        videoHLayout = QHBoxLayout()
        videoHLayout.addWidget(selectButton)
        videoHLayout.addWidget(clearSelectedButton)
        videoVLayout = QVBoxLayout()
        videoVLayout.addLayout(videoHLayout)
        videoVLayout.addWidget(self.videoFileListWidget)

        projectVLayout.addWidget(videoLabel)
        projectVLayout.addLayout(videoVLayout)

        projectVLayout.addWidget(dialogButtonBox)
        self.setLayout(projectVLayout)
        self.nameLineEdit.textEdited.connect(self.name_check)
        self.connect(self.locationComboBox,
                     SIGNAL("activated(int)"),
                     self.locationComboBox.browse_folder)
        self.connect(self.locationComboBox,
                     SIGNAL("currentIndexChanged(int)"), self.location_check)
        selectButton.clicked.connect(self.select_files)
        clearSelectedButton.clicked.connect(self.clear_files)

    def select_files(self):
        fileNames, extension = (QFileDialog.getOpenFileNames(
                     self, "Browse to select file",
                     "C:\workspace\\vista\project\ctdot_test",
                     "Video Files (*.mp4 *.avi)")
                     )
        self.videoFileListWidget.add_text_list(fileNames)

    def clear_files(self):
        selectedItems = self.videoFileListWidget.selectedItems()
        self.videoFileListWidget.remove_items(selectedItems)

    def name_check(self, text):
        self.nameDummy = self.nameLineEdit.check(text)
        self.emit(SIGNAL("completeChanged()"))

    def location_check(self, int):
        if self.locationComboBox.currentText() == '':
            self.locationDummy = False
        else:
            self.locationDummy = True
        self.emit(SIGNAL("completeChanged()"))

    def accept(self):
        QDialog.accept(self)


class VDetectParamsDialog(QDialog):
    def __init__(self, videosDf, parent=None):
        QDialog.__init__(self, parent)

        self.move(0, 0)
        self.setMinimumSize(1300, 600)

        # Definining all the widgets for defining the parameters
        videoLabel = QLabel("Name:")
        self.videoLineEdit = QLineEdit()
        self.videoLineEdit.setReadOnly(True)
        videoLabel.setBuddy(self.videoLineEdit)

        startRegionLabel = QLabel("a. Start Region:")
        self.startRegionLineEdit = QLineEdit()
        startRegionLabel.setBuddy(self.startRegionLineEdit)
        startRegionConfigure = QPushButton()
        startRegionConfigure.setIcon(QIcon("../images/drawregion.png"))
        hStartRegionHLayout = QHBoxLayout()
        hStartRegionHLayout.addWidget(startRegionLabel)
        hStartRegionHLayout.addWidget(self.startRegionLineEdit)
        hStartRegionHLayout.addWidget(startRegionConfigure)

        endRegionLabel = QLabel("b. End Region:")
        self.endRegionLineEdit = QLineEdit()
        endRegionLabel.setBuddy(self.endRegionLineEdit)
        endRegionConfigure = QPushButton()
        endRegionConfigure.setIcon(QIcon("../images/drawregion.png"))
        hEndRegionHLayout = QHBoxLayout()
        hEndRegionHLayout.addWidget(endRegionLabel)
        hEndRegionHLayout.addWidget(self.endRegionLineEdit)
        hEndRegionHLayout.addWidget(endRegionConfigure)

        leftOverlayRegionLabel = QLabel("c. Left Overlay Region:")
        self.leftOverlayRegionLineEdit = QLineEdit()
        leftOverlayRegionLabel.setBuddy(self.leftOverlayRegionLineEdit)
        leftOverlayRegionConfigure = QPushButton()
        leftOverlayRegionConfigure.setIcon(QIcon("../images/drawregion.png"))
        hLeftOverlayRegionHLayout = QHBoxLayout()
        hLeftOverlayRegionHLayout.addWidget(leftOverlayRegionLabel)
        hLeftOverlayRegionHLayout.addWidget(self.leftOverlayRegionLineEdit)
        hLeftOverlayRegionHLayout.addWidget(leftOverlayRegionConfigure)

        rightOverlayRegionLabel = QLabel("d. Right Overlay Region:")
        self.rightOverlayRegionLineEdit = QLineEdit()
        rightOverlayRegionLabel.setBuddy(self.rightOverlayRegionLineEdit)
        rightOverlayRegionConfigure = QPushButton()
        rightOverlayRegionConfigure.setIcon(QIcon("../images/drawregion.png"))
        hRightOverlayRegionHLayout = QHBoxLayout()
        hRightOverlayRegionHLayout.addWidget(rightOverlayRegionLabel)
        hRightOverlayRegionHLayout.addWidget(self.rightOverlayRegionLineEdit)
        hRightOverlayRegionHLayout.addWidget(rightOverlayRegionConfigure)

        bufferSizeLabel = QLabel("e. Buffer size:")
        self.bufferSizeSpinBox = QSpinBox()
        self.bufferSizeSpinBox.setMinimum(0)
        self.bufferSizeSpinBox.setMaximum(100)
        self.bufferSizeSpinBox.setValue(2)

        minObjectSizeDayLabel = QLabel("""f. Minimum size of """
                                       """the object for day time tracking:""")
        self.minObjectSizeDaySpinBox = QSpinBox()
        self.minObjectSizeDaySpinBox.setMinimum(0)
        self.minObjectSizeDaySpinBox.setMaximum(10000)
        self.minObjectSizeDaySpinBox.setValue(5000)

        minObjectSizeNightLabel = QLabel("""g. Minimum size of the """
                                         """object for night time tracking:""")
        self.minObjectSizeNightSpinBox = QSpinBox()
        self.minObjectSizeNightSpinBox.setMinimum(0)
        self.minObjectSizeNightSpinBox.setMaximum(500)
        self.minObjectSizeNightSpinBox.setValue(10)

        skipLabel = QLabel("h. Frames to skip")
        self.skipSpinBox = QSpinBox()
        self.skipSpinBox.setMinimum(0)
        self.skipSpinBox.setMaximum(10)
        self.skipSpinBox.setValue(3)

        learningTimeLabel = QLabel("i. Learning time")
        self.learningTimeSpinBox = QSpinBox()
        self.learningTimeSpinBox.setMinimum(0)
        self.learningTimeSpinBox.setMaximum(1000)
        self.learningTimeSpinBox.setValue(240)

        expectedDistLabel = QLabel("j. Expected distance")
        self.expectedDistanceSpinBox = QSpinBox()
        self.expectedDistanceSpinBox.setMinimum(0)
        self.expectedDistanceSpinBox.setMaximum(100)
        self.expectedDistanceSpinBox.setValue(20)

        horizontalBandwidthLabel = QLabel("k. Horizontal Bandwidth")
        self.horizontalBandwidthSpinBox = QSpinBox()
        self.horizontalBandwidthSpinBox.setMinimum(0)
        self.horizontalBandwidthSpinBox.setMaximum(10)
        self.horizontalBandwidthSpinBox.setValue(50)

        nmixturesLabel = QLabel("l. Number Mixtures")
        self.nmixturesSpinBox = QSpinBox()
        self.nmixturesSpinBox.setMinimum(0)
        self.nmixturesSpinBox.setMaximum(10)
        self.nmixturesSpinBox.setValue(5)

        backgroundratioLabel = QLabel("m. Background ratio")
        self.backgroundratioLineEdit = QLineEdit()
        self.backgroundratioLineEdit.setText("0.6")

        detectShadowsLabel = QLabel("n. Detect Shadows")
        self.detectShadowsCBox = ComboBox()
        detectShadowsValuesDict = {"True": True, "False": False}
        self.detectShadowsCBox.add_items(detectShadowsValuesDict)

        nightTimeLabel = QLabel("o. Night time")
        self.nightTimeCBox = ComboBox()
        nightTimeValuesDict = {"True": True, "False": False}
        self.nightTimeCBox.add_items(nightTimeValuesDict)

        # Pandas df object containing the information about videos
        self.videosDf = videosDf
        self.videosDf.fillna("", inplace=True)

        # Setup the model
        self.setup_model()

        # setting up the mapper for viewing
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)

        # TODO: This is hard coded needs to be modified so the
        # widget objects can be mapped to the columns
        self.mapper.addMapping(self.videoLineEdit, 0)
        self.mapper.addMapping(self.startRegionLineEdit, 1)
        self.mapper.toFirst()

        # Implementing the video player
        videoPlayerLabel = QLabel("Video Player:")
        self.video = Phonon.VideoWidget(self)
        self.video.setMinimumSize(720, 480)
        # self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self)
        self.media = Phonon.MediaObject(self)
        # Phonon.createPath(self.media, self.audio)
        Phonon.createPath(self.media, self.video)

        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon("../images/play.png"))
        self.playButton.setToolTip("play")
        self.playButton.setEnabled(False)
        self.pauseButton = QPushButton()
        self.pauseButton.setEnabled(False)
        self.pauseButton.setIcon(QIcon("../images/pause.png"))
        self.pauseButton.setToolTip("pause")
        self.drawPolygonButton = QPushButton()
        # self.drawPolygonButton.setEnabled(False)
        self.drawPolygonButton.setIcon(QIcon("../images/polygon.png"))
        self.drawPolygonButton.setToolTip("define region")

        self.videoSlider = Phonon.SeekSlider()
        self.videoSlider.setMediaObject(self.media)
        self.videoSlider.setToolTip("video slider")

        # buttons for navigating the videos
        self.nextButton = QPushButton("Next")
        self.previousButton = QPushButton("Previous")
        self.previousButton.setEnabled(False)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel |
                                           QDialogButtonBox.Ok)

        # Laying out the mapper object
        vMapperLayout = QVBoxLayout()

        videoHLayout = QHBoxLayout()
        videoHLayout.addWidget(videoLabel)
        videoHLayout.addWidget(self.videoLineEdit)

        vMapperLayout.addLayout(videoHLayout)
        vMapperLayout.addLayout(hStartRegionHLayout)
        vMapperLayout.addLayout(hEndRegionHLayout)
        vMapperLayout.addLayout(hLeftOverlayRegionHLayout)
        vMapperLayout.addLayout(hRightOverlayRegionHLayout)

        bufferSizeHLayout = QHBoxLayout()
        bufferSizeHLayout.addWidget(bufferSizeLabel)
        bufferSizeHLayout.addWidget(self.bufferSizeSpinBox)
        vMapperLayout.addLayout(bufferSizeHLayout)

        minObjectSizeDayHLayout = QHBoxLayout()
        minObjectSizeDayHLayout.addWidget(minObjectSizeDayLabel)
        minObjectSizeDayHLayout.addWidget(self.minObjectSizeDaySpinBox)
        vMapperLayout.addLayout(minObjectSizeDayHLayout)

        minObjectSizeNightHLayout = QHBoxLayout()
        minObjectSizeNightHLayout.addWidget(minObjectSizeNightLabel)
        minObjectSizeNightHLayout.addWidget(self.minObjectSizeNightSpinBox)
        vMapperLayout.addLayout(minObjectSizeNightHLayout)

        skipHLayout = QHBoxLayout()
        skipHLayout.addWidget(skipLabel)
        skipHLayout.addWidget(self.skipSpinBox)
        vMapperLayout.addLayout(skipHLayout)

        learningTimeHLayout = QHBoxLayout()
        learningTimeHLayout.addWidget(learningTimeLabel)
        learningTimeHLayout.addWidget(self.learningTimeSpinBox)
        vMapperLayout.addLayout(learningTimeHLayout)

        expectedDistHLayout = QHBoxLayout()
        expectedDistHLayout.addWidget(expectedDistLabel)
        expectedDistHLayout.addWidget(self.expectedDistanceSpinBox)
        vMapperLayout.addLayout(expectedDistHLayout)

        horizontalBandwidthHLayout = QHBoxLayout()
        horizontalBandwidthHLayout.addWidget(horizontalBandwidthLabel)
        horizontalBandwidthHLayout.addWidget(self.horizontalBandwidthSpinBox)
        vMapperLayout.addLayout(horizontalBandwidthHLayout)

        nmixturesHLayout = QHBoxLayout()
        nmixturesHLayout.addWidget(nmixturesLabel)
        nmixturesHLayout.addWidget(self.nmixturesSpinBox)
        vMapperLayout.addLayout(nmixturesHLayout)

        backgroundratioHLayout = QHBoxLayout()
        backgroundratioHLayout.addWidget(backgroundratioLabel)
        backgroundratioHLayout.addWidget(self.backgroundratioLineEdit)
        vMapperLayout.addLayout(backgroundratioHLayout)

        detectShadowsHLayout = QHBoxLayout()
        detectShadowsHLayout.addWidget(detectShadowsLabel)
        detectShadowsHLayout.addWidget(self.detectShadowsCBox)
        vMapperLayout.addLayout(detectShadowsHLayout)

        nightTimeHLayout = QHBoxLayout()
        nightTimeHLayout.addWidget(nightTimeLabel)
        nightTimeHLayout.addWidget(self.nightTimeCBox)
        vMapperLayout.addLayout(nightTimeHLayout)
        # vMapperLayout.addWidget(startRegionLineEdit)

        # Laying out the player
        vPlayerLayout = QVBoxLayout()
        vPlayerLayout.addWidget(videoPlayerLabel)
        vPlayerLayout.addWidget(self.video)
        hPlayerButtonsLayout = QHBoxLayout()
        hPlayerButtonsLayout.addWidget(self.playButton)
        hPlayerButtonsLayout.addWidget(self.pauseButton)
        hPlayerButtonsLayout.addWidget(self.drawPolygonButton)
        hPlayerButtonsLayout.addWidget(self.videoSlider)
        vPlayerLayout.addLayout(hPlayerButtonsLayout)

        # Organzing the mapper and video player next to each other
        hSplitLayout = QHBoxLayout()
        hSplitLayout.addLayout(vMapperLayout)
        verticalLine = QFrame()
        verticalLine.setFrameStyle(QFrame.VLine)
        hSplitLayout.addWidget(verticalLine)
        hSplitLayout.addLayout(vPlayerLayout)

        # Laying it all out
        hButtonLayout = QHBoxLayout()
        hButtonLayout.addWidget(self.previousButton)
        hButtonLayout.addWidget(self.nextButton)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hSplitLayout)
        vLayout.addLayout(hButtonLayout)
        vLayout.addWidget(dialogButtonBox)

        self.setLayout(vLayout)

        self.previousButton.clicked.connect(self.mapper.toPrevious)
        self.nextButton.clicked.connect(self.mapper.toNext)
        self.mapper.currentIndexChanged.connect(self.update_buttons)
        self.media.stateChanged.connect(self.handle_state_changed)
        self.playButton.clicked.connect(self.play_video)
        self.pauseButton.clicked.connect(self.pause_video)

        startRegionConfigure.clicked.connect(self.draw_start_region)
        endRegionConfigure.clicked.connect(self.draw_end_region)
        (leftOverlayRegionConfigure.clicked.connect(
         self.draw_left_overlay_region))
        (rightOverlayRegionConfigure.clicked.connect(
         self.draw_right_overlay_region))

    def setup_model(self):
        rows, cols = self.videosDf.shape
        print rows, cols
        self.model = QStandardItemModel(rows, cols, self)
        for row in self.videosDf.iterrows():
            for column, columnName in enumerate(self.videosDf.columns):
                # print (row[0], column, "column name",
                #       columnName, row[1][columnName])
                value = row[1][columnName]
                item = QStandardItem(value)
                self.model.setItem(row[0], column, item)

    def update_buttons(self, row):
        self.previousButton.setEnabled(row > 0)
        self.nextButton.setEnabled(row < self.model.rowCount() - 1)
        self.stop_video()

    def play_video(self):
        self.media.play()
        self.playButton.setEnabled(False)
        self.pauseButton.setEnabled(True)

    def pause_video(self):
        self.media.pause()
        self.pauseButton.setEnabled(False)
        self.playButton.setEnabled(True)

    def stop_video(self):
        self.pauseButton.setEnabled(False)
        self.playButton.setEnabled(False)
        self.media.stop()

    def draw_start_region(self):
        self.load_video()

    def draw_end_region(self):
        self.load_video()

    def draw_left_overlay_region(self):
        self.load_video()

    def draw_right_overlay_region(self):
        self.load_video()

    def load_video(self):
        self.stop_video()
        path = self.videoLineEdit.text()
        print path, type(path)
        ms = Phonon.MediaSource(path)
        self.media.setCurrentSource(ms)
        self.media.play()
        self.pauseButton.setEnabled(True)

    def handle_state_changed(self, newstate, oldstate):
        if newstate == Phonon.ErrorState:
            source = self.media.currentSource().fileName()
            QMessageBox.warning(self, ("ERROR: could not play: {0}"
                                       .format(source)))

    def accept(self):
        QDialog.accept(self)


class DebugDialog(QDialog):
    """
    In this page the debugging properties will
    be collected.
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.setFixedSize(QSize(800, 400))

        showLastCarLabel = QLabel("a. Show the last car detected")
        self.showLastCarCBox = ComboBox()
        showLastCarValuesDict = {"True": True, "False": False}
        self.showLastCarCBox.add_items(showLastCarValuesDict)
        showLastCarLabel.setBuddy(self.showLastCarCBox)

        boundBoxesOnLabel = (QLabel(
                             "b. Show the bounding boxes objects detected"))
        self.boundBoxesOnCBox = ComboBox()
        boundBoxesOnValuesDict = {"True": True, "False": False}
        self.boundBoxesOnCBox.add_items(boundBoxesOnValuesDict)
        boundBoxesOnLabel.setBuddy(self.boundBoxesOnCBox)

        predictionOnLabel = QLabel("c. Show the path prediction")
        self.predictionOnCBox = ComboBox()
        predictionOnValuesDict = {"True": True, "False": False}
        self.predictionOnCBox.add_items(predictionOnValuesDict)
        predictionOnLabel.setBuddy(self.predictionOnCBox)

        latestPathOnLabel = QLabel("d. Show latest path")
        self.latestPathOnCBox = ComboBox()
        latestPathOnValuesDict = {"True": True, "False": False}
        self.latestPathOnCBox.add_items(latestPathOnValuesDict)
        latestPathOnLabel.setBuddy(self.latestPathOnCBox)

        displayTransitLedgerLabel = QLabel("e. Show transit ledger")
        self.displayTransitLedgerCBox = ComboBox()
        displayTransitLedgerValuesDict = {"True": True, "False": False}
        self.displayTransitLedgerCBox.add_items(displayTransitLedgerValuesDict)
        displayTransitLedgerLabel.setBuddy(self.displayTransitLedgerCBox)

        displayFocusRegionsLabel = QLabel("e. Show focus regions")
        self.displayFocusRegionsCBox = ComboBox()
        displayFocusRegionsValuesDict = {"True": True, "False": False}
        self.displayFocusRegionsCBox.add_items(displayFocusRegionsValuesDict)
        displayFocusRegionsLabel.setBuddy(self.displayFocusRegionsCBox)

        showPathOfIDLabel = QLabel("e. Show path of specific vehicle ID")
        self.showPathOfIDCBox = ComboBox()
        showPathOfIDValuesDict = {"-1": -1}
        self.showPathOfIDCBox.add_items(showPathOfIDValuesDict)
        showPathOfIDLabel.setBuddy(self.showPathOfIDCBox)

        displayTypeLabel = QLabel("f. Type of debug display")
        self.displayTypeCBox = ComboBox()
        displayTypeValuesDict = {"Use Background": 1,
                                 "Use Orginal Frame": 2,
                                 "Use Resized With Overlays Frame": 3,
                                 "Use subtracted": 4}
        self.displayTypeCBox.add_items(displayTypeValuesDict)
        displayTypeLabel.setBuddy(self.displayTypeCBox)

        dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel |
                                           QDialogButtonBox.Ok)

        debugVLayout = QVBoxLayout()
        debugVLayout.addWidget(showLastCarLabel)
        debugVLayout.addWidget(self.showLastCarCBox)
        debugVLayout.addWidget(boundBoxesOnLabel)
        debugVLayout.addWidget(self.boundBoxesOnCBox)
        debugVLayout.addWidget(predictionOnLabel)
        debugVLayout.addWidget(self.predictionOnCBox)
        debugVLayout.addWidget(latestPathOnLabel)
        debugVLayout.addWidget(self.latestPathOnCBox)
        debugVLayout.addWidget(displayTransitLedgerLabel)
        debugVLayout.addWidget(self.displayTransitLedgerCBox)
        debugVLayout.addWidget(displayFocusRegionsLabel)
        debugVLayout.addWidget(self.displayFocusRegionsCBox)
        debugVLayout.addWidget(showPathOfIDLabel)
        debugVLayout.addWidget(self.showPathOfIDCBox)
        debugVLayout.addWidget(displayTypeLabel)
        debugVLayout.addWidget(self.displayTypeCBox)
        debugVLayout.addWidget(dialogButtonBox)

        self.setLayout(debugVLayout)

    def accept(self):
        QDialog.accept(self)

if __name__ == '__main__':
    import sys
    import pandas as pd
    import numpy as np
    app = QApplication(sys.argv)
    videosDf = pd.read_csv("videoDf.csv", header=0)

    window = VDetectParamsWidget(videosDf)
    window.show()
    sys.exit(app.exec_())
