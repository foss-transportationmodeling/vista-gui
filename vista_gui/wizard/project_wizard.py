import sys
import os
import pandas as pd

from PySide.QtGui import *
from PySide.QtCore import *
import random
import yaml
from windows.widgets import *


class ProjectOptionsPage(QWizardPage):
    def __init__(self, wiz, parent=None, title="", maWin=None):
        QWizardPage.__init__(self, parent)
        self.wiz = wiz
        self.setTitle(title)

        self.maWin = maWin

        nameLabel = QLabel("a. Enter project name")
        self.nameLineEdit = LineEdit()
        nameLabel.setBuddy(self.nameLineEdit)

        locationLabel = QLabel("b. Select a project file location")
        self.locationComboBox = ComboBoxFolder()
        (self.locationComboBox.addItems(
         ["Browse to select folder..."]))

        locationLabel.setBuddy(self.locationComboBox)

        descLabel = QLabel("c. Enter project description (Optional)")
        self.descTextEdit = QTextEdit()
        descLabel.setBuddy(self.descTextEdit)

        videoLabel = QLabel("d. Select traffic video(s) for this project")
        self.selectButton = QPushButton("Select")
        clearSelectedButton = QPushButton("Clear")
        self.videoFileListWidget = ListWidget(extendedSelection=True)
        self.selectButton.setEnabled(False)

        projectVLayout = QVBoxLayout()
        projectVLayout.addWidget(nameLabel)
        projectVLayout.addWidget(self.nameLineEdit)
        projectVLayout.addWidget(locationLabel)
        projectVLayout.addWidget(self.locationComboBox)
        projectVLayout.addWidget(descLabel)
        projectVLayout.addWidget(self.descTextEdit)

        videoHLayout = QHBoxLayout()
        videoHLayout.addWidget(self.selectButton)
        videoHLayout.addWidget(clearSelectedButton)
        videoVLayout = QVBoxLayout()
        videoVLayout.addLayout(videoHLayout)
        videoVLayout.addWidget(self.videoFileListWidget)

        projectVLayout.addWidget(videoLabel)
        projectVLayout.addLayout(videoVLayout)

        self.setLayout(projectVLayout)
        self.nameLineEdit.textEdited.connect(self.name_check)
        self.connect(self.locationComboBox,
                     SIGNAL("activated(int)"),
                     self.locationComboBox.browse_folder)
        self.connect(self.locationComboBox,
                     SIGNAL("currentIndexChanged(int)"), self.location_check)
        self.selectButton.clicked.connect(self.select_files)
        clearSelectedButton.clicked.connect(self.clear_files)

        self.data = {'project_name': self.nameLineEdit.text(),
                     'project_location': self.locationComboBox.itemText(0),
                     'project_description': self.descTextEdit.toPlainText(),
                     'project_videos': [
                        self.videoFileListWidget.item(i).text()
                        for i in range(self.videoFileListWidget.count())]}

    def select_files(self):
        fileNames, extension = (QFileDialog.getOpenFileNames(
                     self, "Browse to select file",
                     self.locationComboBox.currentText(),
                     "Video Files (*.wmv *.avi)")
                     )
        print fileNames
        self.videoFileListWidget.add_text_list(fileNames)
        self.wiz.vDetectParamsPage.page_update()

    def clear_files(self):
        selectedItems = self.videoFileListWidget.selectedItems()
        self.videoFileListWidget.remove_items(selectedItems)

    def name_check(self, text):
        self.nameDummy = self.nameLineEdit.check(text)
        self.emit(SIGNAL("completeChanged()"))

    def location_check(self, int):
        self.selectButton.setEnabled(True)
        if self.locationComboBox.currentText() == '':
            self.locationDummy = False
        else:
            self.locationDummy = True
        self.emit(SIGNAL("completeChanged()"))

    def populateYaml(self):
        self.maWin.project_location = os.path.join(
            self.locationComboBox.currentText(), self.nameLineEdit.text())

        self.data = {
            'project_name': self.nameLineEdit.text(),
            'project_location': self.locationComboBox.itemText(0),
            'project_description': self.descTextEdit.toPlainText(),
            'project_videos': [
                self.videoFileListWidget.item(i).text()
                for i in range(self.videoFileListWidget.count())]}

        dire = os.path.join(self.maWin.project_location, 'data')

        try:
            open(os.path.join(dire, "test.txt"), 'w').close()
        except:
            os.makedirs(dire)

        open(os.path.join(dire, 'project_options.yaml'), 'w').close()
        stream = file(os.path.join(dire, 'project_options.yaml'), 'w')
        yaml.dump(self.data, stream)
        print(yaml.dump(self.data))

    def populateFields(self):
        try:
            dire = (os.path.join(self.maWin.project_location, 'data'))

            stream = file(os.path.join(dire, 'project_options.yaml'), 'r')
            self.data = yaml.load(stream)
            self.nameLineEdit.setText(self.data['project_name'])
            self.locationComboBox.insertItem(0, self.data['project_location'])
            self.locationComboBox.setCurrentIndex(0)
            self.descTextEdit.setText(self.data['project_description'])
            for item in self.data['project_videos']:
                self.videoFileListWidget.addItem(item)
        except:
            print("No Save Data!")


class VDetectParamsPage(QWizardPage):
    def __init__(self, projectPage, maWin, parent=None):
        QWizardPage.__init__(self, parent)
        self.projectPage = projectPage
        self.maWin = maWin
        self.setTitle("Step 2: Enter the parameters for vehicle detection")

        # Definining all the widgets for defining the parameters
        videoLabel = QLabel("Name:")
        self.videoLineEdit = QLineEdit()
        self.videoLineEdit.setReadOnly(True)
        videoLabel.setBuddy(self.videoLineEdit)

        startRegionLabel = QLabel("a. Start Region:")
        self.startRegionLineEdit = QLineEdit()
        startRegionLabel.setBuddy(self.startRegionLineEdit)
        startRegionConfigure = QPushButton()
        startRegionConfigure.setIcon(QIcon("./images/drawregion.png"))
        hStartRegionHLayout = QHBoxLayout()
        hStartRegionHLayout.addWidget(startRegionLabel)
        hStartRegionHLayout.addWidget(self.startRegionLineEdit)
        hStartRegionHLayout.addWidget(startRegionConfigure)

        endRegionLabel = QLabel("b. End Region:")
        self.endRegionLineEdit = QLineEdit()
        endRegionLabel.setBuddy(self.endRegionLineEdit)
        endRegionConfigure = QPushButton()
        endRegionConfigure.setIcon(QIcon("./images/drawregion.png"))
        hEndRegionHLayout = QHBoxLayout()
        hEndRegionHLayout.addWidget(endRegionLabel)
        hEndRegionHLayout.addWidget(self.endRegionLineEdit)
        hEndRegionHLayout.addWidget(endRegionConfigure)

        leftOverlayRegionLabel = QLabel("c. Left Overlay Region:")
        self.leftOverlayRegionLineEdit = QLineEdit()
        leftOverlayRegionLabel.setBuddy(self.leftOverlayRegionLineEdit)
        leftOverlayRegionConfigure = QPushButton()
        leftOverlayRegionConfigure.setIcon(QIcon("./images/drawregion.png"))
        hLeftOverlayRegionHLayout = QHBoxLayout()
        hLeftOverlayRegionHLayout.addWidget(leftOverlayRegionLabel)
        hLeftOverlayRegionHLayout.addWidget(self.leftOverlayRegionLineEdit)
        hLeftOverlayRegionHLayout.addWidget(leftOverlayRegionConfigure)

        rightOverlayRegionLabel = QLabel("d. Right Overlay Region:")
        self.rightOverlayRegionLineEdit = QLineEdit()
        rightOverlayRegionLabel.setBuddy(self.rightOverlayRegionLineEdit)
        rightOverlayRegionConfigure = QPushButton()
        rightOverlayRegionConfigure.setIcon(QIcon("./images/drawregion.png"))
        hRightOverlayRegionHLayout = QHBoxLayout()
        hRightOverlayRegionHLayout.addWidget(rightOverlayRegionLabel)
        hRightOverlayRegionHLayout.addWidget(self.rightOverlayRegionLineEdit)
        hRightOverlayRegionHLayout.addWidget(rightOverlayRegionConfigure)

        self.overlayRegions = {
            'start': self.startRegionLineEdit,
            'end': self.endRegionLineEdit,
            'left': self.leftOverlayRegionLineEdit,
            'right': self.rightOverlayRegionLineEdit}

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

        # Implementing the video player
        videoPlayerLabel = QLabel("Video Player:")
        self.video = VWidget(self)
        self.video.setMinimumSize(720, 480)
        self.video.setMaximumSize(720, 480)
        # self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self)
        self.media = Phonon.MediaObject(self)
        # Phonon.createPath(self.media, self.audio)
        Phonon.createPath(self.media, self.video)

        self.clearButton = QPushButton()
        self.clearButton.setEnabled(False)
        self.clearLastButton = QPushButton()
        self.clearLastButton.setEnabled(False)
        self.video.update()
        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon("./images/play.png"))
        self.playButton.setToolTip("play")
        self.playButton.setEnabled(False)
        self.pauseButton = QPushButton()
        self.pauseButton.setEnabled(False)
        self.pauseButton.setIcon(QIcon("./images/pause.png"))
        self.pauseButton.setToolTip("pause")
        self.drawPolygonButton = QPushButton()
        # self.drawPolygonButton.setEnabled(False)
        self.drawPolygonButton.setIcon(QIcon("./images/polygon.png"))
        self.drawPolygonButton.setToolTip("define region")
        self.drawPolygonButton.setEnabled(False)

        self.videoSlider = Phonon.SeekSlider()
        self.videoSlider.setMediaObject(self.media)
        self.videoSlider.setToolTip("video slider")

        # buttons for navigating the videos
        self.nextButton = QPushButton("Next")
        self.previousButton = QPushButton("Previous")
        self.previousButton.setEnabled(False)

        # Sets up model
        self.page_update()

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
        hPlayerButtonsLayout.addWidget(self.clearLastButton)
        hPlayerButtonsLayout.addWidget(self.clearButton)
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

        self.setLayout(vLayout)

        self.clearButton.clicked.connect(self.clearDots)
        self.clearLastButton.clicked.connect(self.clearLastDot)
        self.media.stateChanged.connect(self.handle_state_changed)
        self.playButton.clicked.connect(self.play_video)
        self.pauseButton.clicked.connect(self.pause_video)
        self.drawPolygonButton.clicked.connect(self.draw_polygon)

        # Current region for poly select
        self.currentRegion = None
        self.drawState = False

        startRegionConfigure.clicked.connect(self.draw_start_region)
        endRegionConfigure.clicked.connect(self.draw_end_region)
        leftOverlayRegionConfigure.clicked.connect(
            self.draw_left_overlay_region)
        rightOverlayRegionConfigure.clicked.connect(
            self.draw_right_overlay_region)

        self.setup_data()  # Setup Data to populate fields

    def clearDots(self):
        self.video.clear()

    def clearLastDot(self):
        self.video.clearLast()

    def updateRegionFields(self):
        if not(self.currentRegion is None):
            dots = self.video.getDots(self.currentRegion)
            s = ""
            for i in dots:
                if i[2] == 0 and i[3] == 0:
                    break
                else:
                    # Need to add tol
                    size = self.video.size().toTuple()
                    x = i[0]
                    y = i[1]
                    x = 0 if x < 0 else x
                    y = 0 if y < 0 else y
                    x = size[0] if x >= size[0] - 20 else x
                    y = size[1] if y >= size[1] - 20 else y
                    s += '({},{})'.format(x, y)
                    s += ';'
            self.overlayRegions[self.currentRegion].setText(s[:len(s)-1])

    def page_update(self):
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
        self.previousButton.clicked.connect(self.vidShiftPre)
        self.nextButton.clicked.connect(self.vidShiftPre)
        self.previousButton.clicked.connect(self.mapper.toPrevious)
        self.nextButton.clicked.connect(self.mapper.toNext)
        self.previousButton.clicked.connect(self.vidShiftPost)
        self.nextButton.clicked.connect(self.vidShiftPost)
        self.mapper.currentIndexChanged.connect(self.update_buttons)

    def vidShiftPre(self):
        print(self.mapper.currentIndex())
        self.populateYaml()
        self.video.clearAll()
        print('shifted')

    def vidShiftPost(self):
        try:
            self.populateFields()
            for i in self.overlayRegions:
                pre = self.overlayRegions[i].text()
                if pre != "" and pre[0] == '(':
                    points = pre.split(';')
                    dots = []
                    for j in points:
                        p = j.split(',')
                        x = int(p[0][1:])
                        y = int(p[1][:len(p[1]) - 1])
                        dots.append([x, y, 10, 10])
                    self.video.loadCustom(dots, i)
        except:
            print("No Save File Exits")

    def populateYaml(self, dataSet=False):
        if not dataSet:
            self.PageData[self.mapper.currentIndex()] = {
                "Start_Region": self.startRegionLineEdit.text(),
                "End_Region": self.endRegionLineEdit.text(),
                "Left_Region": self.leftOverlayRegionLineEdit.text(),
                "Right_Region": self.rightOverlayRegionLineEdit.text(),
                "Buffer_Size": self.bufferSizeSpinBox.value(),
                "Min_Object_Day": self.minObjectSizeDaySpinBox.value(),
                "Min_Object_Night": self.minObjectSizeNightSpinBox.value(),
                "Frame_Skip": self.skipSpinBox.value(),
                "Learn_Time": self.learningTimeSpinBox.value(),
                "Expected_Dist": self.expectedDistanceSpinBox.value(),
                "Horizontal_Bandwidth":
                    self.horizontalBandwidthSpinBox.value(),
                "Number_Mixtures": self.nmixturesSpinBox.value(),
                "Background_Ratio": self.backgroundratioLineEdit.text(),
                "Detect_Shadows": self.detectShadowsCBox.currentIndex(),
                "Night_Time": self.nightTimeCBox.currentIndex()}

        for i in range(self.vids.count()):
            dire = os.path.join(
                self.maWin.project_location,
                'data',
                'project_params{0}.yaml'.format(str(i)))

            try:
                open(dire, 'w').close()
            except:
                os.makedirs(os.path.join(self.maWin.project_location, 'data'))

            stream = file(dire, 'w')
            yaml.dump(self.PageData[i], stream)

    def populateFields(self):

        for i in range(self.vids.count()):
            dire = os.path.join(
                self.maWin.project_location,
                'data',
                'project_params{0}.yaml'.format(str(i)))

            open(dire, 'r').close()
            stream = file(dire, 'r')
            self.PageData[i] = yaml.load(stream)
            self.loadFields()

    def loadFields(self):
        fields = self.PageData[self.mapper.currentIndex()]
        self.startRegionLineEdit.setText(fields["Start_Region"])
        self.endRegionLineEdit.setText(fields["End_Region"])
        self.leftOverlayRegionLineEdit.setText(fields["Left_Region"])
        self.rightOverlayRegionLineEdit.setText(fields["Right_Region"])
        self.bufferSizeSpinBox.setValue(fields["Buffer_Size"])
        self.minObjectSizeDaySpinBox.setValue(fields["Min_Object_Day"])
        self.minObjectSizeNightSpinBox.setValue(fields["Min_Object_Night"])
        self.skipSpinBox.setValue(fields["Frame_Skip"])
        self.learningTimeSpinBox.setValue(fields["Learn_Time"])
        self.expectedDistanceSpinBox.setValue(fields["Expected_Dist"])
        self.horizontalBandwidthSpinBox.setValue(
            fields["Horizontal_Bandwidth"])
        self.nmixturesSpinBox.setValue(fields["Number_Mixtures"])
        self.backgroundratioLineEdit.setText(fields["Background_Ratio"])
        self.detectShadowsCBox.setCurrentIndex(fields["Detect_Shadows"])
        self.nightTimeCBox.setCurrentIndex(fields["Night_Time"])

    def setup_model(self):
        self.vids = self.projectPage.videoFileListWidget
        count = self.vids.count()

        self.model = QStandardItemModel(count, 2, self)
        self.PageData = [None for i in range(self.vids.count())]

        for i in range(count):
            value = QStandardItem()
            value.setText(self.vids.item(i).text())
            self.model.setItem(i, 0, value)
            val = QStandardItem()
            val.setText("")
            self.model.setItem(i, 1, val)

    def setup_data(self):
        try:
            self.populateFields()
        except:
            # self.populateFields()
            self.PageData = [{
                "Start_Region": "",
                "End_Region": "",
                "Left_Region": "",
                "Right_Region": "",
                "Buffer_Size": 2,
                "Min_Object_Day": 5000,
                "Min_Object_Night": 10,
                "Frame_Skip": 3,
                "Learn_Time": 240,
                "Expected_Dist": 20,
                "Horizontal_Bandwidth": 50,
                "Number_Mixtures": 5,
                "Background_Ratio": "0.6",
                "Detect_Shadows": 0,
                "Night_Time": 0} for i in range(self.vids.count())]

        self.populateYaml(True)

    def update_buttons(self, row):
        self.previousButton.setEnabled(row > 0)
        self.nextButton.setEnabled(row < self.model.rowCount() - 1)
        self.stop_video()

    def play_video(self):
        self.media.play()
        self.playButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.drawPolygonButton.setEnabled(True)
        self.video_control_buttons()

    def pause_video(self):
        self.media.pause()
        self.pauseButton.setEnabled(False)
        self.playButton.setEnabled(True)
        self.drawPolygonButton.setEnabled(True)
        self.video_control_buttons()

    def stop_video(self):
        self.pauseButton.setEnabled(False)
        self.playButton.setEnabled(False)
        self.drawPolygonButton.setEnabled(False)
        self.video_control_buttons()
        self.media.stop()

    def video_control_buttons(self):
        self.clearButton.setEnabled(False)
        self.clearLastButton.setEnabled(False)
        self.video.polydraw = False
        self.drawState = False
        self.updateRegionFields()

    def draw_polygon(self):
        if self.drawState:
            self.pause_video()
        else:
            self.media.pause()
            self.pauseButton.setEnabled(False)
            self.playButton.setEnabled(True)
            self.drawPolygonButton.setEnabled(True)
            self.clearButton.setEnabled(True)
            self.clearLastButton.setEnabled(True)
            self.video.polydraw = True
            self.drawState = True

    def draw_start_region(self):
        self.currentRegion = 'start'
        self.draw_region()

    def draw_end_region(self):
        self.currentRegion = 'end'
        self.draw_region()

    def draw_left_overlay_region(self):
        self.currentRegion = 'left'
        self.draw_region()

    def draw_right_overlay_region(self):
        self.currentRegion = 'right'
        self.draw_region()

    def draw_region(self):
        self.video.unload()
        self.load_video()
        self.video.load(self.currentRegion)
        self.drawState = False

    def load_video(self):
        self.stop_video()
        path = self.videoLineEdit.text()
        print path, type(path)
        ms = Phonon.MediaSource(path)
        self.media.setCurrentSource(ms)
        self.media.play()
        self.pauseButton.setEnabled(True)
        self.drawPolygonButton.setEnabled(True)

    def handle_state_changed(self, newstate, oldstate):
        if newstate == Phonon.ErrorState:
            source = self.media.currentSource().fileName()
            QMessageBox.warning(self, "Box",
                                "ERROR: could not play: {0}".format(source))


class DebugPage(QWizardPage):
    def __init__(self, parent=None):
        QWizardPage.__init__(self, parent)

        self.setTitle("Step 3: Enter debugging options")

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

        self.setLayout(debugVLayout)

    def populateYaml(self):
        QMessageBox.warning(self, "Debug Options: YAML",
                            "Yet to implement writing YAML file")

    def populateFields(self):
        QMessageBox.warning(self, "Debug Options: YAML",
                            "Yet to implement populate fields from YAML file")


# New Project Wizard
class Wizard(QWizard):
    def __init__(self, main, parent=None):
        QWizard.__init__(self, parent)
        self.setWindowTitle("Project Setup Wizard")
        self.setWizardStyle(QWizard.ClassicStyle)

        self.move(0, 0)
        # self.setMinimumSize(1300, 700)

        self.projectOptionsPage = ProjectOptionsPage(
            self, title="Step 1: Enter VISTA project details", maWin=main)
        # try:
        #     self.projectOptionsPage.populateFields()
        # except: pass

        # In this page the fileName, saveImgTo, dataBase properties will
        # be defined
        self.addPage(self.projectOptionsPage)

        self.vDetectParamsPage = VDetectParamsPage(
            self.projectOptionsPage, maWin=main)
        # try:
        #     self.vDetectParamsPage.populateFields()
        # except: pass

        self.addPage(self.vDetectParamsPage)

        self.debugPage = DebugPage()
        self.addPage(self.debugPage)

        # Customize wizard buttons
        self.button(QWizard.NextButton).clicked.disconnect()
        self.button(QWizard.NextButton).clicked.connect(self.popYAML)
        self.button(QWizard.FinishButton).clicked.connect(self.popYAML)

        # Setup for YAML export/improt
        self.pages = [
            self.projectOptionsPage, self.vDetectParamsPage, self.debugPage]

        """
        vDetectParamsPage =
        # In this page all parameters related to vehicle detection page
        # including
        # bufferSize
        # minObjectSizeDay
        # minObjectSizeNight
        # skip
        # learningTime
        # fps
        # expectedDist
        # horizontalBandwidth
        # useMOG2
        # nmixtures
        # backgroundratio,
        # detectShadows

        # Left overlay
        # Right overlay
        # startRegion
        # endRegion

        debugPage =
        # showLastCar
        # boundBoxesOn
        # predictionOn,
        # latestPathsOn
        # displayTransitLedger
        # displayFocusRegions,
        # showPathofId
        # displayType
        """
    def popYAML(self):
        try:
            self.pages[self.currentId()].populateYaml()
        except Exception, e:
            print("Load Error: {0}".format(e))
        self.next()


# Used for Configuration Wizards
class ConfigWizard(QWizard):
    def __init__(self, page, title="", parent=None):
        QWizard.__init__(self, parent)
        self.setWindowTitle(title)
        self.setWizardStyle(QWizard.ClassicStyle)
        self.move(0, 0)
        self.page = page
        self.addPage(self.page)
        self.button(QWizard.FinishButton).clicked.connect(self.popYAML)

    def popYAML(self):
        try:
            self.page.populateYaml()
        except Exception, e:
            print("Load Error:{0}".format(e))


def main():
    app = QApplication(sys.argv)
    wiz = Wizard()
    cwiz = ConfigWizard()
    cwiz.show()
    wiz.show()
    app.exec_()

if __name__ == "__main__":
    main()
