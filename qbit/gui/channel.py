
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

		self.banned = []

		self.is_op = False
		self.is_voiced = False

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
		self.channelUserDisplay.installEventFilter(self)

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

	# Context menus
	def eventFilter(self, source, event):

		# User List Menu
		if (event.type() == QtCore.QEvent.ContextMenu and source is self.channelUserDisplay):

			item = source.itemAt(event.pos())
			if item is None: return True

			user = item.text()
			if '@' in user:
				user_op = True
			else:
				user_op = False
			if '+' in user:
				user_voiced = True
			else:
				user_voiced = False
			user = user.replace("@","")
			user = user.replace("+","")
			user = user.replace("%","")
			user = user.replace("~","")
			user = user.replace("&","")

			if user == self.parent.nickname:
				if not self.is_op:
					if not self.is_voiced:
						return True
				menu = QMenu()
				actDeop = menu.addAction(QIcon(IMAGE_MINUS_ICON),'De-op self')
				actDevoice = menu.addAction(QIcon(IMAGE_MINUS_ICON),'De-voice self')
				if self.is_op:
					actDevoice.setVisible(False)
				if self.is_voiced:
					actDeop.setVisible(False)
				action = menu.exec_(self.channelUserDisplay.mapToGlobal(event.pos()))
				if action == actDeop:
					self.parent.irc.connection.send_items('MODE', self.channel, "-o", self.parent.nickname)
					return True
				if action == actDevoice:
					self.parent.irc.connection.send_items('MODE', self.channel, "-v", self.parent.nickname)
					return True
				return True

			menu = QMenu()

			if self.is_op:
				infoChan = menu.addAction(QIcon(IMAGE_USER_ICON),'Channel Operator')
			elif self.is_voiced:
				infoChan = menu.addAction(QIcon(IMAGE_USER_ICON),'Voiced User')
			else:
				infoChan = menu.addAction(QIcon(IMAGE_USER_ICON),'Normal User')

			infoChan.setFont(self.parent.fontBoldItalic)
			menu.addSeparator()

			actMsg = menu.addAction(QIcon(IMAGE_PAGE_ICON),'Message User')
			actNotice = menu.addAction(QIcon(IMAGE_PAGE_ICON),'Notice User')

			if self.is_op: menu.addSeparator()

			actOp = menu.addAction(QIcon(IMAGE_PLUS_ICON),'Give ops')
			actDeop = menu.addAction(QIcon(IMAGE_MINUS_ICON),'Take ops')

			actVoice = menu.addAction(QIcon(IMAGE_PLUS_ICON),'Give voice')
			actDevoice = menu.addAction(QIcon(IMAGE_MINUS_ICON),'Take voice')

			if user_op:
				actOp.setVisible(False)
			else:
				actDeop.setVisible(False)

			if user_voiced:
				actVoice.setVisible(False)
			else:
				actDevoice.setVisible(False)

			actKick = menu.addAction('Kick user')
			actBan = menu.addAction('Ban user')

			if len(self.banned)>0:
				if self.is_op:
					menuBanned = menu.addMenu("Remove Ban")
					for u in self.banned:
						action = menuBanned.addAction(QIcon(IMAGE_USER_ICON),f"{u}")
						action.triggered.connect(
							lambda state,user=u: self.unban(user))

			if not self.is_op:
				actOp.setVisible(False)
				actDeop.setVisible(False)
				actVoice.setVisible(False)
				actDevoice.setVisible(False)
				actKick.setVisible(False)
				actBan.setVisible(False)

			menu.addSeparator()

			actClip = menu.addAction(QIcon(IMAGE_CLIPBOARD_ICON),'Copy nick to clipboard')
			actUClip = menu.addAction(QIcon(IMAGE_CLIPBOARD_ICON),'Copy user list to clipboard')

			action = menu.exec_(self.channelUserDisplay.mapToGlobal(event.pos()))

			if action == actMsg:
				self.userTextInput.setText(f"/msg {user} ")
				self.userTextInput.setFocus()
				return True

			if action == actNotice:
				self.userTextInput.setText(f"/notice {user} ")
				self.userTextInput.setFocus()
				return True

			if action == actOp:
				self.parent.irc.connection.send_items('MODE', self.channel, "+o", user)
				return True

			if action == actDeop:
				self.parent.irc.connection.send_items('MODE', self.channel, "-o", user)
				return True

			if action == actVoice:
				self.parent.irc.connection.send_items('MODE', self.channel, "+v", user)
				return True

			if action == actDevoice:
				self.parent.irc.connection.send_items('MODE', self.channel, "-v", user)
				return True

			if action == actKick:
				self.parent.irc.connection.send_items('KICK', self.channel, user)
				return True

			if action == actBan:
				uh = self.getUserHostmask(user)
				if uh == None:
					self.parent.irc.connection.send_items('MODE', self.channel, "+b", user)
					self.banned.append(user)
				else:
					self.parent.irc.connection.send_items('MODE', self.channel, "+b", f"*@{uh}")
					self.banned.append(f"*@{uh}")
				return True

			if action == actClip:
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText(user, mode=cb.Clipboard)
				return True

			if action == actUClip:
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText("\n".join(self.userlist), mode=cb.Clipboard)
				return True

		return super(Viewer, self).eventFilter(source, event)

	def unban(self,user):
		self.parent.irc.connection.send_items('MODE', self.channel, "-b", user)
		bc = []
		for u in self.banned:
			if u == user: continue
			bc.append(u)
		self.banned = bc

	def getUserHostmask(self,nick):
		for u in self.userlist:
			if '!' in u:
				up = u.split('!')
				if nick == up[0]:
					m = up[1].split('@')
					return m[1]
		return None

	def setUserList(self,ulist):
		self.channelUserDisplay.clear()
		self.userlist = []
		for n in ulist:
			u = NickMask(n)

			# Strip channel status symbols for storage
			ue = u
			if ue[0]=='@': ue = ue.replace('@','',1)
			if ue[0]=='+': ue = ue.replace('+','',1)
			if ue[0]=='~': ue = ue.replace('~','',1)
			if ue[0]=='&': ue = ue.replace('&','',1)
			if ue[0]=='%': ue = ue.replace('%','',1)
			self.userlist.append(ue)

			# Check for client channel status
			if u.nick == self.parent.nickname:
				self.is_op = False
				self.is_voiced = False
			if u.nick == f"@{self.parent.nickname}": self.is_op = True
			if u.nick == f"+{self.parent.nickname}": self.is_voiced = True
			
			# Add nick to the user display
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
