
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

from irc.client import NickMask

from qbit.common import *

class Viewer(QMainWindow):

	def getType(self):
		return self.type

	def __init__(self,app,restart_func,channel,client,parent=None):
		super(Viewer, self).__init__(parent)

		self.app = app
		self.restart_program = restart_func
		self.channel = channel
		self.client = client
		self.parent = parent
		self.type = "channel"

		self.userlist = []

		self.info = [channel,'',0,0,0,0,0,0,0,0]

		self.topic = ''

		self.buildInterface()

	def buildInterface(self):
		#self.setWindowTitle(self.title)

		#self.STATUS = self.statusBar()

		self.channelTopic = QLineEdit("")
		self.channelTopic.setAlignment(Qt.AlignLeft)
		self.channelTopic.setStyleSheet("background-color:transparent; border: 0px solid #000000;")
		self.channelTopic.returnPressed.connect(self.changeTopic)

		# Main window
		self.channelChatDisplay = QTextBrowser(self)
		self.channelChatDisplay.setObjectName("channelChatDisplay")

		self.channelChatDisplay.anchorClicked.connect(self.linkClicked)

		self.channelUserDisplay = QListWidget(self)
		self.channelUserDisplay.setObjectName("channelUserDisplay")

		self.userTextInput = QLineEdit(self)
		self.userTextInput.setObjectName("userTextInput")
		self.userTextInput.returnPressed.connect(self.handleUserInput)

		# Layout
		self.horizontalSplitter = QSplitter(Qt.Horizontal)
		self.horizontalSplitter.addWidget(self.channelChatDisplay)
		self.horizontalSplitter.addWidget(self.channelUserDisplay)
		self.horizontalSplitter.setSizes([400,100])

		self.verticalSplitter = QSplitter(Qt.Vertical)
		self.verticalSplitter.addWidget(self.horizontalSplitter)
		self.verticalSplitter.addWidget(self.userTextInput)
		self.verticalSplitter.setSizes([475,25])

		self.channelChatDisplay.setFont(self.parent.font)
		self.channelUserDisplay.setFont(self.parent.fontBold)
		self.userTextInput.setFont(self.parent.font)

		self.channelTopic.setContentsMargins(0, 0, 0, 0)
		self.channelChatDisplay.setContentsMargins(0, 0, 0, 0)
		self.channelUserDisplay.setContentsMargins(0, 0, 0, 0)
		self.userTextInput.setContentsMargins(0, 0, 0, 0)
		self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
		self.verticalSplitter.setContentsMargins(0, 0, 0, 0)

		finalLayout = QVBoxLayout()
		finalLayout.setContentsMargins(0, 0, 0, 0)
		finalLayout.addWidget(self.channelTopic)
		finalLayout.addWidget(self.verticalSplitter)

		x = QWidget()
		x.setLayout(finalLayout)
		self.setCentralWidget(x)

		self.userTextInput.setFocus()

		# self.setCentralWidget(self.verticalSplitter)


	def setUserList(self,ulist):
		self.channelUserDisplay.clear()
		for n in ulist:
			u = NickMask(n)
			self.channelUserDisplay.addItem(u.nick)

	def cleanUserList(self,ulist):
		self.channelUserDisplay.clear()

	def addUser(self,data):
		self.channelUserDisplay.addItem(data)

	def hasUser( self, text ):
		for u in [str(self.channelUserDisplay.item(i).text()) for i in range(self.channelUserDisplay.count())]:
			u = u.replace('@','')
			u = u.replace('+','')
			u = u.replace('~','')
			u = u.replace('&','')
			u = u.replace('%','')
			if u == text: return True
		return False


	def removeUser( self, text ):
		items = self.channelUserDisplay.findItems(text,Qt.MatchExactly)
		if len(items) > 0:
			for item in items:
				self.channelUserDisplay.takeItem(self.channelUserDisplay.row(item))

	def writeText(self,text):
		self.channelChatDisplay.append(text)
		self.channelChatDisplay.moveCursor(QTextCursor.End)

	# Handle user input
	def handleUserInput(self):
		user_input = self.userTextInput.text()
		self.userTextInput.setText('')

		self.parent.handleUserInput(self.channel,user_input)

	# Handle user input
	def changeTopic(self):
		# print(self.channelTopic.text())
		# user_input = self.channelTopic.text()
		# user_input.strip()

		# if self.channelTopic.text().isspace():
		# 	self.parent.userChangeTopic(self.channel,"")
		# 	return

		self.parent.userChangeTopic(self.channel,self.channelTopic.text())
		self.userTextInput.setFocus()

	def setTopic(self,topic):
		self.channelTopic.setText(topic)
		if not topic.isspace():
			self.topic = topic

	# If users click on URLs, they will open in the default browser
	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			QDesktopServices.openUrl(url)
			self.channelChatDisplay.setSource(QUrl())

	# Exit the program if the window is closed
	def closeEvent(self, event):
		self.app.quit()
