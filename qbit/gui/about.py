
# Qbit IRC Client
# Copyright (C) 2019  Daniel Hetrick

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from qbit.common import *

class Dialog(QDialog):

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		self.setWindowTitle(f"About {APPLICATION_NAME}")
		self.setWindowIcon(QIcon(IMAGE_QBIT_ICON))

		logo = QLabel()
		pixmap = QPixmap(IMAGE_LOGO)
		logo.setPixmap(pixmap)
		logo.setAlignment(Qt.AlignCenter)

		gpl_logo = QLabel()
		pixmap = QPixmap(IMAGE_GPL)
		gpl_logo.setPixmap(pixmap)
		gpl_logo.setAlignment(Qt.AlignCenter)

		py_logo = QLabel()
		pixmap = QPixmap(IMAGE_PYTHON)
		py_logo.setPixmap(pixmap)
		py_logo.setAlignment(Qt.AlignCenter)

		qt_logo = QLabel()
		pixmap = QPixmap(IMAGE_QT)
		qt_logo.setPixmap(pixmap)
		qt_logo.setAlignment(Qt.AlignCenter)

		technology = QHBoxLayout()
		technology.addWidget(py_logo)
		technology.addWidget(gpl_logo)
		technology.addWidget(qt_logo)

		ainfo = QLabel(f"Version {APPLICATION_VERSION}")
		ainfo.setAlignment(Qt.AlignCenter)

		ilink = QLabel("<a href=\"https://github.com/danhetrick\">https://github.com/danhetrick</a>")
		ilink.setAlignment(Qt.AlignCenter)
		ilink.setOpenExternalLinks(True)

		irclib = QLabel("<a href=\"https://github.com/jaraco/irc\">Python IRC Library</a> by <a href=\"mailto:jaraco@jaraco.com\">Jason R. Coombs</a>")
		irclib.setAlignment(Qt.AlignCenter)
		irclib.setOpenExternalLinks(True)

		colourlib = QLabel("<a href=\"https://github.com/vaab/colour\">Python Colour Library</a> by Valentin Lab")
		colourlib.setAlignment(Qt.AlignCenter)
		colourlib.setOpenExternalLinks(True)

		icons = QLabel("<a href=\"https://material.io/tools/icons/\">Icons</a> by <a href=\"https://google.com\">Google</a>")
		icons.setAlignment(Qt.AlignCenter)
		icons.setOpenExternalLinks(True)

		spacer = QLabel(" ")

		aexit = QPushButton("Ok")
		aexit.clicked.connect(self.close)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(logo)
		finalLayout.addWidget(ainfo)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(irclib)
		finalLayout.addWidget(colourlib)
		finalLayout.addWidget(icons)
		finalLayout.addWidget(spacer)
		finalLayout.addLayout(technology)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(ilink)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(aexit)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
