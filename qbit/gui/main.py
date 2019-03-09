
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

from qbit.irc import QbitClient

import qbit.gui.channel as Channel
import qbit.gui.user as User
import qbit.gui.connect as Connect

import qbit.gui.about as AboutDialog

from irc.client import NickMask

from qbit.common import *

class Viewer(QMainWindow):

	def helpText(self):
		ht = []
		ht.append("")
		ht.append(f"<b><i>{APPLICATION_NAME} {APPLICATION_VERSION} Commands</i></b>")
		ht.append("")
		ht.append("<b>/msg <i>TARGET MESSAGE</i></b>")
		ht.append("&nbsp;&nbsp;Sends a message to a user or channel.")
		ht.append("")
		ht.append("<b>/notice <i>TARGET MESSAGE</i></b>")
		ht.append("&nbsp;&nbsp;Sends a notice to a user or channel.")
		ht.append("")
		ht.append("<b>/nick <i>NEW_NICKNAME</i></b>")
		ht.append("&nbsp;&nbsp;Changes the nickname in use. If the chosen nickname is already in use, \"_\" is appended to the nickname until an unused nickname is found.")
		ht.append("")
		ht.append("<b>/ignore <i>TARGET</i></b>")
		ht.append("&nbsp;&nbsp;Any messages sent by the targeted nickname or channel will be ignored, and not displayed. Issue the <b>/ignore</b> command with the same target to turn ignore off.")
		ht.append("")
		ht.append("<b>/join <i>CHANNEL [KEY]</i></b>")
		ht.append("&nbsp;&nbsp;Joins a channel. <b><i>KEY</i></b> is only needed if the channel is locked (+k) with a key.")
		ht.append("")
		ht.append("<b>/part <i>CHANNEL</i></b>")
		ht.append("&nbsp;&nbsp;Leaves a channel.")
		return ht

	def helpTextChannel(self):
		t = self.helpText()
		t.append("")
		t.append("<b>/me <i>MESSAGE</i></b>")
		t.append("&nbsp;&nbsp;Sends a CTCP action message to the current channel or user.")
		return t

	def handleUserInput(self,source,text):

		if source == "":
			# base page
			tokens = text.split()

			if len(tokens)==1 and tokens[0] == "/help":
				for l in self.helpText():
					d = system_display(l)
					self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/ignore":
				if len(tokens)==2:
					tokens.pop(0)
					nick = tokens.pop(0)
					if self.isIgnored(nick):
						self.unignoreUser(nick)
						d = system_display(f"{nick} is no longer ignored.")
						self.basePage.writeText(d)
					else:
						self.ignoreUser(nick)
						d = system_display(f"{nick} is ignored.")
						self.basePage.writeText(d)
					return
				d = error_display("USAGE: /ignore NICK")
				self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/nick":
				if len(tokens)==2:
					tokens.pop(0)
					nick = tokens[0]
					self.irc.connection.nick(nick)
					self.nickname = nick
					self.refresh_all_users()
					return
				d = error_display("USAGE: /nick NEW_NICKNAME")
				self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/msg":
				if len(tokens)>=3:
					tokens.pop(0)
					target = tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.privmsg(target,msg)
					if target in self.pages:
						w = self.pages[target]
						d = mychat_display(self.nickname,msg,self.maxnicklength)
						w.writeText(d)
					return
				d = error_display("USAGE: /msg TARGET MESSAGE")
				self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/notice":
				if len(tokens)>=3:
					tokens.pop(0)
					target = tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.notice(target,msg)
					if target in self.pages:
						w = self.pages[target]
						d = notice_display(self.nickname,msg,self.maxnicklength)
						w.writeText(d)
					return
				d = error_display("USAGE: /notice TARGET MESSAGE")
				self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/join":
				tokens.pop(0)
				if len(tokens)==1:
					self.irc.connection.join(tokens[0])
					return
				elif len(tokens)==2:
					self.irc.connection.join(tokens[0],tokens[1])
					return
				d = error_display("USAGE: /join CHANNEL [KEY]")
				self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/part":
				tokens.pop(0)
				if len(tokens)==1:
					self.irc.connection.part(tokens[0])
					self.removePage(tokens[0])
					return
				elif len(tokens)>1:
					chan = tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.part(chan,msg)
					self.removePage(chan)
					return
				d = error_display("USAGE: /part CHANNEL [MSG]")
				self.basePage.writeText(d)
				return
		else:
			ischannel = False
			if source[0] == "#": ischannel = True
			if source[0] == "&": ischannel = True

			tokens = text.split()

			if len(tokens)==1 and tokens[0] == "/help":
				w = self.pages[source]
				for l in self.helpTextChannel():
					d = system_display(l)
					w.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/ignore":
				if len(tokens)==2:
					tokens.pop(0)
					nick = tokens.pop(0)
					if self.isIgnored(nick):
						self.unignoreUser(nick)
						w = self.pages[source]
						d = system_display(f"{nick} is no longer ignored.")
						w.writeText(d)
					else:
						self.ignoreUser(nick)
						w = self.pages[source]
						d = system_display(f"{nick} is ignored.")
						w.writeText(d)
					return
				if len(tokens)==1:
					if ischannel:
						d = error_display("USAGE: /ignore NICK")
						w = self.pages[source]
						w.writeText(d)
						return
					if self.isIgnored(source):
						self.unignoreUser(source)
						w = self.pages[source]
						d = system_display(f"{source} is no longer ignored.")
						w.writeText(d)
					else:
						self.ignoreUser(source)
						w = self.pages[source]
						d = system_display(f"{source} is ignored.")
						w.writeText(d)
					return
				w = self.pages[source]
				d = error_display("USAGE: /ignore NICK")
				w.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/msg":
				if len(tokens)>=3:
					tokens.pop(0)
					target = tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.privmsg(target,msg)
					if target in self.pages:
						w = self.pages[target]
						d = mychat_display(self.nickname,msg,self.maxnicklength)
						w.writeText(d)
					return
				w = self.pages[source]
				d = error_display("USAGE: /msg TARGET MESSAGE")
				w.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/notice":
				if len(tokens)>=3:
					tokens.pop(0)
					target = tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.notice(target,msg)
					if target in self.pages:
						w = self.pages[target]
						d = notice_display(self.nickname,msg,self.maxnicklength)
						w.writeText(d)
					return
				d = error_display("USAGE: /notice TARGET MESSAGE")
				self.basePage.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/me":
				if len(tokens)>1:
					tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.action(source,msg)
					w = self.pages[source]
					d = action_display(self.nickname,msg)
					w.writeText(d)
					return
				w = self.pages[source]
				d = error_display("USAGE: /me MESSAGE")
				w.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/join":
				tokens.pop(0)
				if len(tokens)==1:
					self.irc.connection.join(tokens[0])
					return
				elif len(tokens)==2:
					self.irc.connection.join(tokens[0],tokens[1])
					return
				w = self.pages[source]
				d = error_display("USAGE: /join CHANNEL [KEY]")
				w.writeText(d)
				return

			if len(tokens)>=1 and tokens[0] == "/part":
				tokens.pop(0)
				if len(tokens)==1:
					self.irc.connection.part(tokens[0])
					self.removePage(tokens[0])
					return
				elif len(tokens)==0:
					if ischannel: self.irc.connection.part(source)
					self.removePage(source)
					return
				elif len(tokens)>1:
					chan = tokens.pop(0)
					msg = ' '.join(tokens)
					self.irc.connection.part(chan,msg)
					self.removePage(chan)
					return

			if len(tokens)>=1 and tokens[0] == "/nick":
				if len(tokens)==2:
					tokens.pop(0)
					nick = tokens[0]
					self.irc.connection.nick(nick)
					self.nickname = nick
					self.refresh_all_users()
					return
				d = error_display("USAGE: /nick NEW_NICKNAME")
				self.basePage.writeText(d)
				return

			self.irc.connection.privmsg(source,text)
			w = self.pages[source]
			d = mychat_display(self.nickname,text,self.maxnicklength)
			w.writeText(d)

	def __init__(self,app,restart_func,title="Qbit",parent=None):
		super(Viewer, self).__init__(parent)

		self.app = app
		self.restart_program = restart_func
		self.title = title

		self.pages = {}

		self.online = False

		self.maxnicklength = MAX_USERNAME_SIZE

		self.basePageOpen = False
		self.basePageBuffer = []

		self.unread = []

		self.ignore = []

		self.openNewPages = False
		self.openNewPrivate = True

		self.currentPage = ""

		self.firstchan = ""

		self.loadFont(QBIT_FONT)
		self.app.setFont(self.font)

		self.display = loadDisplayConfig()

		self.buildUI()

	def buildUI(self):
		self.setWindowTitle(self.title)
		self.setWindowIcon(QIcon(IMAGE_QBIT_ICON))

		self.menubar = self.menuBar()
		self.menubar.setVisible(False)

		appMenu = self.menubar.addMenu("Qbit")

		optOpenNew = QAction("View new messages",self,checkable=True)
		optOpenNew.setChecked(self.openNewPages)
		optOpenNew.triggered.connect(self.toggleOpenNew)
		appMenu.addAction(optOpenNew)

		optOpenPrivate = QAction("View new private messages",self,checkable=True)
		optOpenPrivate.setChecked(self.openNewPrivate)
		optOpenPrivate.triggered.connect(self.toggleOpenPrivate)
		appMenu.addAction(optOpenPrivate)

		appMenu.addSeparator()

		self.appAbout = QAction(QIcon(IMAGE_ABOUT_ICON),"About Qbit",self)
		self.appAbout.triggered.connect(self.show_about)
		appMenu.addAction(self.appAbout)

		appMenu.addSeparator()

		self.appRestart = QAction(QIcon(IMAGE_RESTART_ICON),"Restart Qbit",self)
		self.appRestart.triggered.connect(self.restart_program)
		appMenu.addAction(self.appRestart)

		self.appExit = QAction(QIcon(IMAGE_EXIT_ICON),"Exit",self)
		self.appExit.triggered.connect(self.close)
		appMenu.addAction(self.appExit)

		self.unreadMenu = self.menubar.addMenu("Unread Messages")
		action = self.unreadMenu.addAction(f"No unread messages")
		action.setFont(self.fontItalic)

		self.appRestart.setShortcut('Ctrl+S')
		self.appExit.setShortcut('Ctrl+Q')

		# Page/Channel/User selector
		self.stackSelect = QComboBox(self)
		self.stackSelect.activated.connect(self.setPage)
		self.stackSelect.setFont(self.bigfontBold)

		self.stackSelect.setVisible(False)

		# Page display
		self.stack = QStackedWidget(self)

		mainLayout = QVBoxLayout()
		mainLayout.addWidget(self.stackSelect)
		mainLayout.addWidget(self.stack)

		mainBox = QWidget()
		mainBox.setContentsMargins(0, 0, 0, 0)
		mainBox.setLayout(mainLayout)

		self.setCentralWidget(mainBox)

		self.resize(INITIAL_WINDOW_WIDTH,INITIAL_WINDOW_HEIGHT)

		# Add connect page
		pageConnect = QWidget()
		self.connectPage = Connect.Viewer(self)
		conLayout = QVBoxLayout()
		conLayout.addWidget(self.connectPage)
		pageConnect.setLayout(conLayout)
		self.stack.addWidget(pageConnect)

	def createBasePage(self,title):

		pageUser = QWidget()
		gui = User.Viewer(self.app,self.restart_program,"",self)

		userLayout = QVBoxLayout()
		userLayout.addWidget(gui)

		gui.channelChatDisplay.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")
		gui.userTextInput.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")

		pageUser.setLayout(userLayout)

		self.stack.addWidget(pageUser)

		self.stackSelect.addItem(QIcon(IMAGE_SERVER_ICON),f" {title}")

		return gui

	def addChannelPage(self,channel,icon=None):

		pageChannel = QWidget()
		gui = Channel.Viewer(self.app,self.restart_program,channel,self.irc.connection,self)

		channelLayout = QVBoxLayout()
		channelLayout.addWidget(gui)

		gui.channelChatDisplay.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")
		gui.userTextInput.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")
		gui.channelUserDisplay.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")

		pageChannel.setLayout(channelLayout)

		self.stack.addWidget(pageChannel)

		self.stackSelect.addItem(QIcon(IMAGE_PAGE_ICON),f" {channel}")

		self.pages[channel] = gui

	def addUserPage(self,channel,icon=None):

		pageUser = QWidget()
		gui = User.Viewer(self.app,self.restart_program,channel,self)

		channelLayout = QVBoxLayout()
		channelLayout.addWidget(gui)

		gui.channelChatDisplay.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")
		gui.userTextInput.setStyleSheet(f"background-color: {self.display['background']}; color: {self.display['text']};")

		pageUser.setLayout(channelLayout)

		self.stack.addWidget(pageUser)

		self.stackSelect.addItem(QIcon(IMAGE_USER_ICON),f" {channel}")

		self.pages[channel] = gui

	def show_about(self):
		x = AboutDialog.Dialog(parent=self)
		x.show()

	def toggleOpenNew(self,state):
		self.openNewPages = state

	def toggleOpenPrivate(self,state):
		self.openNewPrivate = state

	def rebuildUnreadMenu(self):
		self.unreadMenu.clear()

		if len(self.unread)==0:
			self.unreadMenu.setTitle("Unread Messages")
			action = self.unreadMenu.addAction(f"No unread messages")
			action.setFont(self.fontItalic)
			return

		for i in self.unread:
			index = i[0]
			chan = i[1]
			cid = f" {chan}"
			if "#" in chan:
				action = self.unreadMenu.addAction(QIcon(IMAGE_PAGE_ICON),f"{chan}")
			else:
				action = self.unreadMenu.addAction(QIcon(IMAGE_USER_ICON),f"{chan}")
			action.triggered.connect(
				lambda state,index=index: self.changePageIndex(index))

		self.unreadMenu.addSeparator()

		self.setRead = QAction(QIcon(IMAGE_CLEAR_ICON),"Clear unread messsages",self)
		self.setRead.triggered.connect(self.clearReadMessages)
		self.unreadMenu.addAction(self.setRead)

		self.setRead.setShortcut('Ctrl+U')

		self.unreadMenu.setTitle(f"Unread Messages ({str(len(self.unread))})")

	def clearReadMessages(self):
		self.unread = []

		for i in range(self.stackSelect.count()):
			if i == 0: continue
			if "#" in self.stackSelect.itemText(i):
				self.stackSelect.setItemIcon(i,QIcon(IMAGE_PAGE_ICON))
			else:
				self.stackSelect.setItemIcon(i,QIcon(IMAGE_USER_ICON))

		self.rebuildUnreadMenu()

	def setPage(self,i):
		self.stack.setCurrentIndex(i)

		#if i != 0: self.stackSelect.setItemIcon(i,QIcon(IMAGE_PAGE_ICON))

		if i != 0:
			if "#" in self.stackSelect.itemText(i):
				self.stackSelect.setItemIcon(i,QIcon(IMAGE_PAGE_ICON))
			else:
				self.stackSelect.setItemIcon(i,QIcon(IMAGE_USER_ICON))

		num = []
		for m in self.unread:
			if m[0] == i: continue
			num.append(m)
		self.unread = num

		self.rebuildUnreadMenu()

		if i == 0:
			w = self.basePage
			self.setWindowTitle(self.title)
		else:
			id = self.stackSelect.itemText(i).strip()
			self.setWindowTitle(id)
			w = self.pages[id]
		
		w.userTextInput.setFocus()
		self.currentPage = w

	def connectToIrc(self,nick,username,ircname,host,port,password,use_ssl,autojoin):

		self.host = host
		self.port = int(port)
		self.nickname = nick

		self.autoJoinChannels = autojoin

		if use_ssl == 1:
			use_ssl = True
		else:
			use_ssl = False

		self.stack.removeWidget(self.stack.widget(0))
		# Add connecting page
		pageConnecting = QWidget()
		gui = Connecting(self)
		conLayout = QVBoxLayout()
		conLayout.addWidget(gui)
		pageConnecting.setLayout(conLayout)
		self.stack.addWidget(pageConnecting)

		self.irc = QbitClient(self,host,int(port),nick,password,username,ircname,use_ssl)

		self.irc.users.connect(self.gotChannelUserlist)
		self.irc.connected.connect(self.gotWelcome)
		self.irc.pubmsg.connect(self.gotPublicMessage)
		self.irc.privmsg.connect(self.gotPrivateMessage)
		self.irc.actionmsg.connect(self.gotCTCPAction)
		self.irc.joined.connect(self.gotUserJoin)
		self.irc.parted.connect(self.gotUserPart)
		self.irc.mynick.connect(self.gotQbitNick)
		self.irc.motdmsg.connect(self.gotMotd)
		self.irc.clientjoined.connect(self.gotQbitJoinedChannel)
		self.irc.notice.connect(self.gotNotice)
		self.irc.nicklength.connect(self.gotNicklength)
		self.irc.network.connect(self.gotNetwork)
		#self.irc.disconnected.connect(self.disconnected)
		self.irc.ircerror.connect(self.gotServerError)
		self.irc.currenttopic.connect(self.gotCurrentTopic)
		self.irc.topicsetter.connect(self.gotTopicSetter)
		self.irc.topic.connect(self.gotChannelTopic)
		self.irc.channelinfo.connect(self.gotChannelInfo)
		self.irc.usermode.connect(self.gotUserMode)
		self.irc.channelmode.connect(self.gotChannelMode)

		self.irc.nickchange.connect(self.gotNickChange)

		self.irc.start()

	def connectDialog(self):
		x = ConnectDialog.Dialog()
		connection_info = x.get_connect_information(parent=self)

		if not connection_info:
			# User hit cancel button in dialog
			return

		nick = connection_info[0]
		username = connection_info[1]
		realname = connection_info[2]
		host = connection_info[3]
		port = connection_info[4]
		password = connection_info[5]
		use_ssl = connection_info[6]

		self.connectToIrc(nick,username,realname,host,port,password,use_ssl)

	def refresh_all_users(self):
		for c in self.pages:
			if len(c)>0:
				if c[0] == "#":
					self.irc.refresh_users(c)
					continue
				if c[0] == "&":
					self.irc.refresh_users(c)
					continue

	def changePage(self,id):
		x = self.getComboStackIndex(f" {id}")
		self.stack.setCurrentIndex(x)
		self.stackSelect.setCurrentIndex(x)
		w = self.pages[id]
		w.userTextInput.setFocus()

		if x==0:
			self.setWindowTitle(self.title)
		else:
			self.setWindowTitle(id)

		self.currentPage = w

	def changePageIndex(self,index):
		self.stack.setCurrentIndex(index)
		self.stackSelect.setCurrentIndex(index)

		if "#" in self.stackSelect.itemText(index):
			self.stackSelect.setItemIcon(index,QIcon(IMAGE_PAGE_ICON))
		else:
			self.stackSelect.setItemIcon(index,QIcon(IMAGE_USER_ICON))

		#self.stackSelect.setItemIcon(index,QIcon(IMAGE_PAGE_ICON))

		num = []
		for i in self.unread:
			if i[0] == index: continue
			num.append(i)
		self.unread = num
		self.rebuildUnreadMenu()

	def samePage(self,id):
		x = self.getComboStackIndex(f" {id}")
		if x == self.stackSelect.currentIndex():
			return True
		else:
			return False

	def setPageHasMessages(self,pid):
		x = self.getComboStackIndex(f" {pid}")
		#self.stackSelect.setItemIcon(x,QIcon(IMAGE_MESSAGES_ICON))

		if "#" in self.stackSelect.itemText(x):
			self.stackSelect.setItemIcon(x,QIcon(IMAGE_PAGE_ICON))
		else:
			self.stackSelect.setItemIcon(x,QIcon(IMAGE_USER_ICON))

		for m in self.unread:
			if m[0] == x: return
		um = [x,pid]
		#print(um)
		self.unread.append(um)

	def setPageNoMessages(self,id):
		x = self.getComboStackIndex(f" {id}")
		#self.stackSelect.setItemIcon(x,QIcon(IMAGE_PAGE_ICON))

		if "#" in self.stackSelect.itemText(x):
			self.stackSelect.setItemIcon(x,QIcon(IMAGE_PAGE_ICON))
		else:
			self.stackSelect.setItemIcon(x,QIcon(IMAGE_USER_ICON))

	def removePage(self,id):
		id = f" {id}"
		x = self.getComboStackIndex(id)
		if not x >= 0: return
		if self.stackSelect.currentIndex() == x:
			y = x - 1
			if y < 0: y = 0
		else:
			y = self.stackSelect.currentIndex()
		w = self.stack.widget(x)
		self.stack.removeWidget(w)
		self.stackSelect.removeItem(x)
		del self.pages[id.strip()]
		self.stack.setCurrentIndex(y)
		self.stackSelect.setCurrentIndex(y)

	def renamePage(self,id,newid):
		sid = f" {id}"
		x = self.getComboStackIndex(sid)
		if x == self.stackSelect.currentIndex():
			movePage = True
		else:
			movePage = False
		if not x >= 0: return
		w = self.stack.widget(x)
		self.stack.removeWidget(w)
		self.stackSelect.removeItem(x)
		self.stack.addWidget(w)
		self.stackSelect.addItem(QIcon(IMAGE_USER_ICON),f" {newid}")

		self.pages[newid] = self.pages[id]
		self.pages[newid].user = newid
		del self.pages[id]

		if movePage:
			n = self.getComboStackIndex(f" {newid}")
			self.setPage(n)
			self.stackSelect.setCurrentIndex(n)

	def getComboStackIndex(self,channel):
		index = 0
		for entry in [self.stackSelect.itemText(i) for i in range(self.stackSelect.count())]:
			if channel == entry: return index
			index = index + 1
		return -1

	def userChangeTopic(self,channel,topic):
		if topic == "": topic = " "
		self.irc.connection.topic(channel,topic)

	def loadFont(self,ufont):

		self.font = QFont(ufont,NORMAL_FONT_SIZE)
		self.fontBold = QFont(ufont,NORMAL_FONT_SIZE,QFont.Bold)
		self.fontItalic = QFont(ufont,NORMAL_FONT_SIZE,QFont.Normal,True)
		self.fontBoldItalic = QFont(ufont,NORMAL_FONT_SIZE,QFont.Bold,True)

		self.bigfont = QFont(ufont,BIG_FONT_SIZE)
		self.bigfontBold = QFont(ufont,BIG_FONT_SIZE,QFont.Bold)
		self.bigfontItalic = QFont(ufont,BIG_FONT_SIZE,QFont.Normal,True)
		self.bigfontBoldItalic = QFont(ufont,BIG_FONT_SIZE,QFont.Bold,True)

		self.smallfont = QFont(ufont,SMALL_FONT_SIZE)
		self.smallfontBold = QFont(ufont,SMALL_FONT_SIZE,QFont.Bold)
		self.smallfontItalic = QFont(ufont,SMALL_FONT_SIZE,QFont.Normal,True)
		self.smallfontBoldItalic = QFont(ufont,SMALL_FONT_SIZE,QFont.Bold,True)

		self.setFont(self.font)

	def isIgnored(self,user):
		if user in self.ignore: return True
		return False

	def ignoreUser(self,user):
		if user in self.ignore:
			return
		self.ignore.append(user)

	def unignoreUser(self,user):
		if not user in self.ignore:
			return
		iu = []
		for u in self.ignore:
			if u == user: continue
			iu.append(u)
		self.ignore = iu

	# Signals

	@pyqtSlot(list)
	def gotNickChange(self,data):
		oldnick = data[0]
		newnick = data[1]

		for p in self.pages:
			w = self.pages[p]
			if w.type == "channel":
				if w.hasUser(oldnick):
					d = system_display(f"{oldnick} is now known as {newnick}")
					w.writeText(d)
			if w.type == "user":
				if w.user == oldnick:
					d = system_display(f"{oldnick} is now known as {newnick}")
					w.writeText(d)

		self.renamePage(oldnick,newnick)
		self.refresh_all_users()


	@pyqtSlot()
	def gotWelcome(self):
		self.online = True

		# Remove connect page
		self.stack.removeWidget(self.stack.widget(0))

		self.stackSelect.setVisible(True)
		self.menubar.setVisible(True)

		self.basePage = self.createBasePage(f"{self.host}:{str(self.port)}")
		self.basePageOpen = True

		self.currentPage = self.basePage

		if len(self.basePageBuffer)>0:
			for e in self.basePageBuffer:
				self.basePage.writeText(e)
			self.basePageBuffer = []

		for e in self.autoJoinChannels:
			if ':' in e:
				channel = e.split(':')[0]
				key = e.split(':')[1]
				self.irc.connection.join(channel,key)
				if self.firstchan == "": self.firstchan = channel
			else:
				self.irc.connection.join(e)
				if self.firstchan == "": self.firstchan = e

	@pyqtSlot(list)
	def gotUserMode(self,data):
		setter = data[0]
		target = data[1]
		mode = data[2]

		d = system_display(f"{setter} set mode {mode} on {target}")
		self.basePage.writeText(d)

	@pyqtSlot(list)
	def gotChannelMode(self,data):
		setter = data[0]
		target = data[1]

		w = self.pages[target]

		for i in data[2]:
			if i[2] == None:
				mode = f"{i[0]}{i[1]}"
			else:
				mode = f"{i[0]}{i[1]} {i[2]}"
			d = system_display(f"{setter} set mode {mode} on {target}")
			w.writeText(d)

	@pyqtSlot(list)
	def gotChannelInfo(self,data):
		channel_name = data[CHANNEL_INFO_NAME]
		channel_key = data[CHANNEL_INFO_KEY]
		channel_limit = data[CHANNEL_INFO_LIMIT]
		channel_invite_only = data[CHANNEL_INFO_INVITEONLY]
		channel_allow_external = data[CHANNEL_INFO_ALLOWEXTERNAL]
		channel_topic_locked = data[CHANNEL_INFO_TOPICLOCKED]
		channel_protected = data[CHANNEL_INFO_PROTECTED]
		channel_secret = data[CHANNEL_INFO_SECRET]
		channel_moderated = data[CHANNEL_INFO_MODERATED]
		channel_nocolors = data[CHANNEL_INFO_NOCOLORS]

		self.pages[channel_name].info = data

	@pyqtSlot(list)
	def gotCurrentTopic(self,data):
		channel = data[0]
		topic = data[1]

		w = self.pages[channel]
		w.setTopic(topic)
		if not topic.isspace():
			d = system_display(f"Channel topic set to \"{topic}\"")
			w.writeText(d)

	@pyqtSlot(list)
	def gotTopicSetter(self,data):
		channel = data[0]
		nick = data[1]

		w = self.pages[channel]
		if w.topic != '':
			d = system_display(f"Channel topic set by {nick}")
			w.writeText(d)

	@pyqtSlot(list)
	def gotChannelTopic(self,data):
		channel = data[0]
		topic = data[1]
		nick = data[2]
		hostmask = data[3]

		w = self.pages[channel]
		w.setTopic(topic)
		if not topic.isspace():
			d = system_display(f"Channel topic set by {nick} to \"{topic}\"")
			w.writeText(d)
		else:
			d = system_display(f"Blank channel topic set by {nick}")
			w.writeText(d)

	@pyqtSlot(list)
	def gotServerError(self,data):
		err_type = data[0]
		err_target = data[1]
		err_msg = data[2]

		# Display error on the currently open page
		d = error_display(f"{err_type} ({err_target}): {err_msg}")
		self.currentPage.writeText(d)

		if self.basePageOpen:
			d = error_display(f"{err_type} ({err_target}): {err_msg}")
			self.basePage.writeText(d)
		else:
			d = error_display(f"{err_type} ({err_target}): {err_msg}")
			self.basePageBuffer.append(d)

	@pyqtSlot(str)
	def gotQbitJoinedChannel(self,data):
		channel = data

		self.addChannelPage(channel)
		if self.openNewPages:
			self.changePage(channel)
			return
		if self.firstchan == channel:
			self.changePage(channel)

	@pyqtSlot(str)
	def gotNicklength(self,data):
		self.maxnicklength = int(data)
		if self.maxnicklength > MAX_USERNAME_SIZE:
			self.maxnicklength = MAX_USERNAME_SIZE

	@pyqtSlot(str)
	def gotNetwork(self,data):
		self.networkname = data
		self.stackSelect.setItemText(0,f" {data} - {self.host}:{str(self.port)}")

	@pyqtSlot(str)
	def gotQbitNick(self,data):
		self.nickname = data

	@pyqtSlot(list)
	def gotMotd(self,data):
		motd = "<br>".join(data)

		d = motd_display(motd,self.maxnicklength)
		self.basePage.writeText(d)

	@pyqtSlot(list)
	def gotUserPart(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		msg = data[3]
		self.irc.refresh_users(channel)

		w = self.pages[channel]
		if len(msg)>0:
			d = system_display(f"{nick} parted {channel} ({msg}).")
		else:
			d = system_display(f"{nick} parted {channel}.")
		w.writeText(d)

	@pyqtSlot(list)
	def gotUserJoin(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		self.irc.refresh_users(channel)

		w = self.pages[channel]
		d = system_display(f"{nick} joined {channel}.")
		w.writeText(d)

	@pyqtSlot(list)
	def gotPublicMessage(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if nick in self.ignore:
			return

		w = self.pages[channel]
		d = chat_display(nick,message,self.maxnicklength)
		w.writeText(d)

		if not self.samePage(channel):
			if self.openNewPages:
				self.changePage(channel)
				return
			self.setPageHasMessages(channel)
			self.rebuildUnreadMenu()

	@pyqtSlot(list)
	def gotPrivateMessage(self,data):
		target = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if nick in self.ignore:
			return

		if nick in self.pages:
			pass
		else:
			self.addUserPage(nick)


		w = self.pages[nick]
		d = chat_display(nick,message,self.maxnicklength)
		w.writeText(d)

		if not self.samePage(nick):
			if self.openNewPages:
				self.changePage(nick)
				return
			if self.openNewPrivate:
				self.changePage(nick)
				return
			self.setPageHasMessages(nick)
			self.rebuildUnreadMenu()

	@pyqtSlot(list)
	def gotCTCPAction(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		w = self.pages[channel]
		d = action_display(nick,message)
		w.writeText(d)

		if self.openNewPages:
			self.changePage(channel)

	@pyqtSlot(list)
	def gotNotice(self,data):
		target = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if target in self.pages:
			w = self.pages[target]
			d = notice_display(nick,message,self.maxnicklength)
			w.writeText(d)
			if self.openNewPages:
				self.changePage(channel)
		else:
			if self.basePageOpen:
				d = notice_display(nick,message,self.maxnicklength)
				self.basePage.writeText(d)
			else:
				d = notice_display(nick,message,self.maxnicklength)
				self.basePageBuffer.append(d)


	@pyqtSlot(str,list)
	def gotChannelUserlist(self,channel,users):

		w = self.pages[channel]
		w.setUserList(users)

class Connecting(QDialog):

	def __init__(self,parent=None):
		super(Connecting,self).__init__(parent)

		self.parent = parent

		self.spinner = QLabel()
		self.movie = QMovie(IMAGE_SPINNER)
		self.spinner.setMovie(self.movie)
		self.movie.start()

		self.spinner.setAlignment(Qt.AlignCenter)

		self.label = QLabel("Connecting to")
		self.label.setFont(self.parent.bigfontBold)
		self.label.setAlignment(Qt.AlignCenter)

		self.label2 = QLabel(f"{self.parent.host}:{str(self.parent.port)}")
		self.label2.setFont(self.parent.bigfontBold)
		self.label2.setAlignment(Qt.AlignCenter)

		vertLayout = QVBoxLayout()
		vertLayout.addStretch()
		vertLayout.addWidget(self.spinner)
		vertLayout.addWidget(self.label)
		vertLayout.addWidget(self.label2)
		vertLayout.addStretch()

		finalLayout = QHBoxLayout()
		finalLayout.addStretch()
		finalLayout.addLayout(vertLayout)
		finalLayout.addStretch()

		self.setLayout(finalLayout)

		











