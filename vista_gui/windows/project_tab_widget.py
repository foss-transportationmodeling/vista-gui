# -*- coding: utf-8 -*-
from PySide.QtGui import *


class ProjectTabWidget(QTabWidget):
    def __init__(self, config):
        QTabWidget.__init__(self)
