# -*- coding: utf-8 -*-
import os

import pandas as pd
import yaml

from PySide.QtGui import *
from PySide.QtCore import *

from wizard.project_wizard import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)


        self.wizard = Wizard(main = self)
        self.project_location = ""
        self.location_set = False
        self.setWindowTitle("VISTA")
        iconPath = os.path.join(".", "images", "vista.png")
        self.setWindowIcon(QIcon(iconPath))
        self.showMaximized()

        pNewAction = self.create_action("&New Project",
                                        self.project_new,
                                        QKeySequence.New,
                                        "projectnew",
                                        "Create a new VISTA project.")
        pOpenAction = self.create_action("&Open Project",
                                         self.project_open,
                                         QKeySequence.Open,
                                         "projectopen",
                                         "Open an existing VISTA project.")
        self.pSaveAction = self.create_action("&Save Project",
                                              self.project_save,
                                              QKeySequence.Save,
                                              "projectsave",
                                              "Save the current project.")
        self.pCloseAction = self.create_action("&Close Project",
                                               self.project_close,
                                               "Ctrl+C",
                                               "projectclose",
                                               "Close the current project")
        self.quitAction = self.create_action("&Quit",
                                             self.close,
                                             "Ctrl+Q",
                                             "quit",
                                             "Close the application.")

        projectOptionsAction = self.create_action("Project Options",
                                                  self.project_options,
                                                  "VISTA project details")
        vDetectParamsPageAction = (self.create_action(
                                   "Vehicle Detection Configuration",
                                   self.detection_configuration,
                                   "Parameters for vehicle detection"))
        debugPageAction = self.create_action("Debug Options",
                                             self.debug_options,
                                             "For reviewing VISTA processes")

        runVistaAction = (self.create_action(
                          "Run Vehicle Counting",
                          self.run_vista,
                          "Run vehicle detection for one or many videos",
                          iconName="run"))
        stopVistaAction = (self.create_action(
                           "Stop Vehicle Counting",
                           self.stop_vista,
                           "Stop vehicle detection for one or many videos",
                           iconName="stop"))

        exportAction = (self.create_action(
                        "Export data",
                        self.export_data,
                        "Explore the results into a flat file format",
                        iconName="export"))
        analyzeAction = (self.create_action(
                         "Analyze results",
                         self.analyze_data,
                         "Analyze the results",
                         iconName="analyze"))

        helpDocumentationAction = self.create_action("Documentation",
                                                     self.show_documentation,
                                                     iconName="documentation",
                                                     tip="""Display the """
                                                     """documentation of """
                                                     """VISTA.""")
        helpAboutAction = self.create_action("About PopGen",
                                             self.show_about,
                                             tip="""Display software """
                                             """information""")

        # Defining all main menu items
        self.projectMenu = self.menuBar().addMenu("&Project")
        self.configureMenu = self.menuBar().addMenu("&Configure")
        self.runMenu = self.menuBar().addMenu("&Run")
        self.outputsMenu = self.menuBar().addMenu("&Outputs")
        # self.annotateMenu = self.menuBar().addMenu("&Annotate")
        self.helpMenu = self.menuBar().addMenu("&Help")

        # Adding actions to menu items
        self.add_actions(self.projectMenu, [pNewAction, pOpenAction,
                                            self.pSaveAction,
                                            self.pCloseAction,
                                            None, self.quitAction])

        self.add_actions(self.configureMenu, [projectOptionsAction,
                                              vDetectParamsPageAction,
                                              debugPageAction])
        self.add_actions(self.runMenu, [runVistaAction, stopVistaAction])
        self.add_actions(self.outputsMenu, [exportAction, analyzeAction])
        self.add_actions(self.helpMenu, [None, helpDocumentationAction,
                                         None, helpAboutAction])

        # Defining toolbar items
        self.projectToolBar = self.addToolBar("Project")
        self.runToolBar = self.addToolBar("Run")
        self.outputsToolBar = self.addToolBar("Outputs")
        # Adding actions to toolbar items
        self.add_actions(self.projectToolBar, [pNewAction, pOpenAction,
                                               self.pSaveAction,
                                               self.pCloseAction])
        self.add_actions(self.runToolBar, [runVistaAction, stopVistaAction])
        self.add_actions(self.outputsToolBar, [exportAction, analyzeAction])

    def check_if_file_exists(self, filePath):
        if os.path.isfile(filePath):
            return True
        else:
            fullPath = os.path.abspath(filePath)
            print ("Current working directory is: {0}".format(os.getcwd()))
            print ("Icon with path: {0} doesn't exist".format(fullPath))
            return False

    def create_action(self, text, slot=None, shortcut=None, iconName=None,
                      tip=None, checkable=False, disabled=None,
                      signal="triggered()"):
        action = QAction(text, self)
        if iconName is not None:
            iconPath = os.path.join(".", "images", "%s.png" % iconName)
            if self.check_if_file_exists(iconPath):
                action.setIcon(QIcon(iconPath))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        if disabled:
            action.setDisabled(True)

        return action

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def project_new(self):
        self.wizard.setWindowIcon(QIcon("./images/projectnew.png"))

        if self.wizard.exec_():
            pass

    def project_open(self):
        saveDir = QFileDialog.getOpenFileName(
                self, ("Save As..."),
                self.project_location,
                "PopGen File (*.vista)")[0]
        try:
            fileL = file(saveDir,'r')
            s = yaml.load(fileL)
            fileL.close()
            self.project_location = s
        except:
            print("Corrupt File!")

    def project_save(self):
        if self.project_location == "":
            print "No project to save!"
        else:
            saveDir = QFileDialog.getSaveFileName(
                    self, ("Save As..."),
                    self.project_location,
                    "PopGen File (*.vista)")[0]
            fileL = file(saveDir,'w')
            yaml.dump(self.project_location,fileL)
            fileL.close()

    def project_close(self):
        pass

    def close(self):
        QMainWindow.close(self)

    #Creates an instance of configuration wizard with a single page
    def configure_options(self, page, title = ""):
        wiz = configWizard(page, title)
        wiz.setWindowIcon(QIcon("./images/projectnew.png"))
        wiz.setButtonLayout([wiz.CancelButton, wiz.FinishButton])
        wiz.exec_()

    #Project options wizard
    def project_options(self):
        page = ProjectOptionsPage(self.wizard, maWin = self)
        try:
            page.populateFields()
        except: print("No Save Data Exists!")
        self.configure_options(page, "Project Options")

    #Vehicle Detection Configuration wizard
    def detection_configuration(self):
        page = VDetectParamsPage(self.wizard.projectOptionsPage, maWin = self)
        try:
            page.populateFields()
        except: print("No Save Data Exists!")
        self.configure_options(page, "Detection Configuration")

    #Debug options Wizard
    def debug_options(self):
        #page = DebugPage()
        page = VDetectParamsPage()
        self.configure_options(page, "Detect Options")

    def run_vista(self):
        import subprocess
        import time
        import sys
        DETACHED_PROCESS = 0x00000008

        self.pid = (subprocess.Popen(
                    [sys.executable, "C:\workspace\\vista\gui\\vista-gui\\vista_gui\call_vista_core.py"],
                    creationflags=DETACHED_PROCESS))

    def stop_vista(self):
        self.pid.terminate()
        print "Outside the loop and closed the process"

    def export_data(self):
        # tableView = TableView()
        # tableView.show()
        QMessageBox.information(self, "Results", "Export data",
                                QMessageBox.Ok)
        pass

    def analyze_data(self):
        QMessageBox.information(self, "Results", "Analyze data",
                                QMessageBox.Ok)
        pass

    def show_documentation(self):
        QMessageBox.information(self, "Documentation", "Work in progress",
                                QMessageBox.Ok)

    def show_about(self):
        QMessageBox.information(self, "About",
                                """VISTA stands for """
                                """Vision-based Traffic """
                                """Monitoring Application""",
                                QMessageBox.Ok)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.addLibraryPath("C:\Python27\Lib\site-packages\PySide\plugins\sqldrivers")
    app.setApplicationName('VISTA')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
