
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

import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from qbit.common import *

class Viewer(QMainWindow):

	def __init__(self,app,restart_func,user,parent=None):
		super(Viewer, self).__init__(parent)

		self.app = app
		self.restart_program = restart_func
		self.user = user
		self.parent = parent
		self.type = "user"

		self.topic = ''

		self.log = []

		self.buildInterface()

	def buildInterface(self):
		#self.setWindowTitle(self.title)

		# Main window
		self.channelChatDisplay = QTextBrowser(self)
		self.channelChatDisplay.setObjectName("channelChatDisplay")

		self.channelChatDisplay.anchorClicked.connect(self.linkClicked)

		self.userTextInput = QLineEdit(self)
		self.userTextInput.setObjectName("userTextInput")
		self.userTextInput.returnPressed.connect(self.handleUserInput)

		# Layout

		self.verticalSplitter = QSplitter(Qt.Vertical)
		self.verticalSplitter.addWidget(self.channelChatDisplay)
		self.verticalSplitter.addWidget(self.userTextInput)
		self.verticalSplitter.setSizes([475,25])

		self.channelChatDisplay.setFont(self.parent.font)
		self.userTextInput.setFont(self.parent.font)

		self.channelChatDisplay.setContentsMargins(0, 0, 0, 0)
		self.userTextInput.setContentsMargins(0, 0, 0, 0)
		self.verticalSplitter.setContentsMargins(0, 0, 0, 0)

		self.setCentralWidget(self.verticalSplitter)

	def writeText(self,text):
		self.channelChatDisplay.append(text)
		self.channelChatDisplay.moveCursor(QTextCursor.End)

		#self.log.append(remove_html_markup(text))

	# Handle user input
	def handleUserInput(self):
		user_input = self.userTextInput.text()
		self.userTextInput.setText('')

		self.parent.handleUserInput(self.user,user_input)

		# if self.user == "":
		# 	# this is the base tab
		# 	print(f"SERVER TAB: {user_input}")
		# 	return

		# print(user_input)

	# If users click on URLs, they will open in the default browser
	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			QDesktopServices.openUrl(url)
			self.channelChatDisplay.setSource(QUrl())

	# Exit the program if the window is closed
	def closeEvent(self, event):
		self.app.quit()

	def setUserList(self,ulist):
		pass

	def cleanUserList(self,ulist):
		pass

	def addUser(self,data):
		pass

	def removeUser( self, text ):
		pass
