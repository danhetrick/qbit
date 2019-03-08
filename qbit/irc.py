
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
import time

from PyQt5.QtCore import *

import irc.client
import irc.modes
from irc.client import NickMask
from irc.dict import IRCDict
from irc.bot import Channel

from blinker import signal

import ssl

from collections import defaultdict

from qbit.common import *

class QbitClient(QThread):

	pubmsg = pyqtSignal(list)
	privmsg = pyqtSignal(list)
	actionmsg = pyqtSignal(list)
	joined = pyqtSignal(list)
	parted = pyqtSignal(list)
	users = pyqtSignal(str,list)
	motdmsg = pyqtSignal(list)
	mynick = pyqtSignal(str)
	clientjoined = pyqtSignal(str)
	connected = pyqtSignal()
	disconnected = pyqtSignal()
	notice = pyqtSignal(list)
	nicklength = pyqtSignal(str)
	network = pyqtSignal(str)
	ircerror = pyqtSignal(list)
	currenttopic = pyqtSignal(list)
	topicsetter = pyqtSignal(list)
	topic = pyqtSignal(list)
	channelinfo = pyqtSignal(list)
	usermode = pyqtSignal(list)
	channelmode = pyqtSignal(list)

	nickchange = pyqtSignal(list)

	def refresh_users(self,channel):
		self.connection.send_items('NAMES', channel)

	def got_ctopic(self,sender,**kw):
		channel = kw['channel']
		topic = kw['topic']

		pm = [channel,topic]
		self.currenttopic.emit(pm)

	def got_stopic(self,sender,**kw):
		channel = kw['channel']
		nick = kw['nick']

		pm = [channel,nick]
		self.topicsetter.emit(pm)

	def got_topic(self,sender,**kw):
		channel = kw['channel']
		topic = kw['topic']
		nick = kw['nick']
		hostmask = kw['hostmask']

		pm = [channel,topic,nick,hostmask]
		self.topic.emit(pm)

	def pubchat(self,sender,**kw):
		target = kw['target']
		nick = kw['nick']
		hostmask = kw['hostmask']
		msg = kw['msg']

		pm = [target,nick,hostmask,msg]
		self.pubmsg.emit(pm)

	def privchat(self,sender,**kw):
		target = kw['target']
		nick = kw['nick']
		hostmask = kw['hostmask']
		msg = kw['msg']

		pm = [target,nick,hostmask,msg]
		self.privmsg.emit(pm)

	def got_action(self,sender,**kw):
		target = kw['target']
		nick = kw['nick']
		hostmask = kw['hostmask']
		msg = kw['msg']

		pm = [target,nick,hostmask,msg]
		self.actionmsg.emit(pm)

	def join_channel(self,sender,**kw):
		channel = kw['channel']
		nick = kw['nick']
		hostmask = kw['hostmask']

		if nick == self.nickname:
			self.channels[channel] = Channel()
			self.clientjoined.emit(channel)
		else:
			pm = [channel,nick,hostmask]
			self.joined.emit(pm)

	def part_channel(self,sender,**kw):
		channel = kw['channel']
		nick = kw['nick']
		hostmask = kw['hostmask']
		msg = kw['msg']

		pm = [channel,nick,hostmask,msg]
		self.parted.emit(pm)

		# if nick == self.nickname:
		# 	del self.channels[channel]
		# 	if self.cusers[channel]:
		# 		del self.cusers[channel]
		# 	if self.chatlog[channel]:
		# 		del self.chatlog[channel]
		# else:
		# 	self.channels[channel].remove_user(nick)

	def welcome(self,sender,**kw):
		self.connection = sender

		self.connected.emit()

	def channel_users(self,sender,**kw):
		channel = kw['channel']
		users = kw['users']

		for u in users:
		# 	self.channels[channel].add_user(u)
			self.cusers[channel].append(u)

	def motd(self,sender,**kw):
		msg = kw['motd']

		self.motdmsg.emit(msg)

	def endnames(self,sender,**kw):
		channel = kw['channel']

		# Sort users from highest permissions to lowest
		ulist = self.cusers[channel]
		ownlist = []
		adminlist = []
		oplist = []
		halfoplist = []
		vlist = []
		nlist = []
		for u in ulist:
			nu = NickMask(u)
			if '~' in nu.nick:
				ownlist.append(u)
			elif '&' in nu.nick:
				adminlist.append(u)
			elif '@' in nu.nick:
				oplist.append(u)
			elif '%' in nu.nick:
				halfoplist.append(u)
			elif '+' in nu.nick:
				vlist.append(u)
			else:
				nlist.append(u)
		ulist = ownlist+adminlist+oplist+halfoplist+vlist+nlist
		self.users.emit(channel,ulist)

		self.cusers[channel] = []

	def my_nick(self,sender,**kw):
		self.nickname = kw['nick']
		self.mynick.emit(self.nickname)

	def got_mode(self,sender,**kw):
		source = kw['who']
		target = kw['target']
		mlist = kw['mode']

		if not irc.client.is_channel(target):
			return

		info = [source,target,mlist]
		self.channelmode.emit(info)

		sendRefresh = False
		ch = self.channels[target]
		for sign,mode,argument in mlist:
			f = {"+": ch.set_mode, "-": ch.clear_mode}[sign]
			f(mode,argument)
			if sign == "+":
				if mode == "k":
					ch.key = argument
			else:
				if mode == "k":
					ch.key = ''
			if mode == "o": sendRefresh = True
			if mode == "v": sendRefresh = True

		self.channels[target] = ch

		# Build channel info and send it
		info = build_channel_info(target,ch)
		self.channelinfo.emit(info)

		if sendRefresh:
			self.connection.send_items('NAMES', target)

	def got_umode(self,sender,**kw):
		source = kw['who']
		target = kw['target']
		mlist = kw['mode']

		info = [source,target,mlist]
		self.usermode.emit(info)

	def got_nick(self,sender,**kw):
		oldnick = kw['old']
		newnick = kw['new']

		if oldnick == self.nickname:
			self.nickname = newnick
			self.mynick.emit(newnick)

		info = [oldnick,newnick]
		self.nickchange.emit(info)

		# self.connection.send_items('NAMES')

		# for ch in self.channels.values():
		# 	if ch.has_user(oldnick):
		# 		ch.changenick(oldnick,newnick)

	def got_quit(self,sender,**kw):
		msg = kw['msg']
		nick = kw['nick']

		# for ch in self.channels.values():
		# 	if ch.has_user(nick):
		# 		ch.remove_user(nick)

	def join_error(self,sender,**kw):
		error = kw['msg']
		channel = kw['channel']

		pm = ['join',channel,error]
		self.ircerror.emit(pm)

	def chan_error(self,sender,**kw):
		error = kw['msg']
		channel = kw['channel']

		pm = ['channel',channel,error]
		self.ircerror.emit(pm)

	def misc_error(self,sender,**kw):
		error = kw['msg']
		target = kw['target']

		pm = ['misc',target,error]
		self.ircerror.emit(pm)

	def got_notice(self,sender,**kw):
		target = kw['target']
		msg = kw['msg']
		nick = kw['nick']
		hostmask = kw['hostmask']

		pm = [target,nick,hostmask,msg]
		self.notice.emit(pm)

	def got_nicklength(self,sender,**kw):
		l = kw['length']

		self.nicklength.emit(l)

	def got_network(self,sender,**kw):
		n = kw['network']

		self.network.emit(n)

	def got_disco(self,sender,**kw):
		m = kw['msg']

		self.disconnected.emit()

	def __init__(self,gui,server,port,nickname,password=None,username=None,ircname=None,ssl=False):
		QThread.__init__(self)
		self.gui = gui
		self.server = server
		self.port = port
		self.nickname = nickname
		self.password = password
		self.username = username
		self.ircname = ircname
		self.ssl=ssl

		self.irc = None

		self.channels = IRCDict()

		self.cusers = defaultdict(list)

		self.blink_pubmsg = signal("pubmsg")
		self.blink_privmsg = signal("privmsg")
		self.blink_chanjoin = signal("join")
		self.blink_chanpart = signal("part")
		self.blink_registered = signal("registered")
		self.blink_gotnames = signal("names")
		self.blink_gotmotd = signal("motd")
		self.blink_nameend = signal("endnames")
		self.blink_mynick = signal("mynick")
		self.blink_gotmode = signal("mode")
		self.blink_gotumode = signal("umode")
		self.blink_gotnick = signal("newnick")
		self.blink_gotquit = signal("quit")
		self.blink_gotact = signal("action")
		self.blink_joinerror = signal("joinerror")
		self.blink_chanerror = signal("chanerror")
		self.blink_miscerror = signal("miscerror")
		self.blink_notice = signal("notice")
		self.blink_nicklength = signal("nicklen")
		self.blink_network = signal("network")
		self.blink_disconnected = signal("disconnected")
		self.blink_currenttopic = signal("currenttopic")
		self.blink_topicsetter = signal("topicsetter")
		self.blink_topic = signal("topic")

		self.blink_pubmsg.connect(self.pubchat)
		self.blink_privmsg.connect(self.privchat)
		self.blink_chanjoin.connect(self.join_channel)
		self.blink_chanpart.connect(self.part_channel)
		self.blink_registered.connect(self.welcome)
		self.blink_gotnames.connect(self.channel_users)
		self.blink_gotmotd.connect(self.motd)
		self.blink_nameend.connect(self.endnames)
		self.blink_mynick.connect(self.my_nick)
		self.blink_gotmode.connect(self.got_mode)
		self.blink_gotumode.connect(self.got_umode)
		self.blink_gotnick.connect(self.got_nick)
		self.blink_gotquit.connect(self.got_quit)
		self.blink_gotact.connect(self.got_action)
		self.blink_joinerror.connect(self.join_error)
		self.blink_chanerror.connect(self.chan_error)
		self.blink_miscerror.connect(self.misc_error)
		self.blink_notice.connect(self.got_notice)
		self.blink_nicklength.connect(self.got_nicklength)
		self.blink_network.connect(self.got_network)
		self.blink_disconnected.connect(self.got_disco)
		self.blink_currenttopic.connect(self.got_ctopic)
		self.blink_topicsetter.connect(self.got_stopic)
		self.blink_topic.connect(self.got_topic)

	def run(self):
		if self.ssl:
			c_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
		else:
			c_factory = irc.connection.Factory()
		tirc = QbitIRC()
		try:
			tirc.connect(self.server,self.port,self.nickname,password=self.password,username=self.username,ircname=self.ircname,connect_factory=c_factory)
		except irc.client.ServerConnectionError as x:
			print(x)
			sys.exit(1)
		tirc.start()

class QbitIRC(irc.client.SimpleIRCClient):

	def __init__(self):
		irc.client.SimpleIRCClient.__init__(self)
		self.motd = []

	def on_ctcp(self,connection,event):
		user = NickMask(event.source)

		for e in event.arguments:
			if e == "VERSION":
				version_msg = f"\x01VERSION {APPLICATION_NAME} {APPLICATION_VERSION}/{HOST_PLATFORM}\x01"
				self.connection.notice(user.nick,version_msg)
			if e == "TIME":
				localtime = time.asctime( time.localtime(time.time()) )
				tz = time.strftime("%z", time.gmtime())
				self.connection.notice(user.nick,f"\x01TIME {localtime} {tz}\x01")


	def on_notopic(self,connection,event):
		pass

	def on_currenttopic(self,connection,event):

		topic_event = signal("currenttopic")
		topic_event.send(connection,channel=event.arguments[0],topic=event.arguments[1])

	def on_topicinfo(self,connection,event):

		topic_event = signal("topicsetter")
		topic_event.send(connection,channel=event.arguments[0],nick=event.arguments[1])

	def on_topic(self,connection,event):

		user = NickMask(event.source)

		topic_event = signal("topic")
		topic_event.send(connection,channel=event.target,nick=user.nick,hostmask=user.userhost,topic=event.arguments[0])

	def on_disconnect(self,connection,event):
		# This never, ever happens
		disco_event = signal("disconnected")
		disco_event.send(connection,msg="Disconnected from server")

	def on_featurelist(self,connection,event):
		for e in event.arguments:
			fl = e.split(',')
			for l in fl:
				l.strip()
				p = l.split('=')
				if len(p)==2:
					if p[0].lower() == 'maxnicklen':
						feature_event = signal("nicklen")
						feature_event.send(connection,length=p[1])
					if p[0].lower() == 'nicklen':
						feature_event = signal("nicklen")
						feature_event.send(connection,length=p[1])
					if p[0].lower() == 'network':
						feature_event = signal("network")
						feature_event.send(connection,network=p[1])

	def misc_error(self,connection,event):
		target = event.arguments[0]
		error = event.arguments[1]

		merror_event = signal("miscerror")
		merror_event.send(connection,msg=error,target=target)

	def on_nousers(self,connection,event):
		self.misc_error(connection,event)

	def on_nosuchnick(self,connection,event):
		self.misc_error(connection,event)

	def on_nosuchserver(self,connection,event):
		self.misc_error(connection,event)

	def on_nosuchchannel(self,connection,event):
		self.misc_error(connection,event)

	def on_cannotsendtochan(self,connection,event):
		self.misc_error(connection,event)

	def on_toomanychannels(self,connection,event):
		self.misc_error(connection,event)

	def on_toomanytargets(self,connection,event):
		self.misc_error(connection,event)

	def on_unknowncommand(self,connection,event):
		self.misc_error(connection,event)

	def on_erroneusnickname(self,connection,event):
		self.misc_error(connection,event)

	def on_nochanmodes(self,connection,event): # channel doesn't support modes
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("chanerror")
		cerror_event.send(connection,msg=error,channel=channel)
	
	def on_banlistfull(self,connection,event):
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("chanerror")
		cerror_event.send(connection,msg=error,channel=channel)

	def on_chanoprivsneeded(self,connection,event):
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("chanerror")
		cerror_event.send(connection,msg=error,channel=channel)

	def on_channelisfull(self,connection,event):
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("joinerror")
		cerror_event.send(connection,msg=error,channel=channel)

	def on_inviteonlychan(self,connection,event):
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("joinerror")
		cerror_event.send(connection,msg=error,channel=channel)

	def on_bannedfromchan(self,connection,event):
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("joinerror")
		cerror_event.send(connection,msg=error,channel=channel)

	def on_badchannelkey(self,connection,event):
		channel = event.arguments[0]
		error = event.arguments[1]

		cerror_event = signal("joinerror")
		cerror_event.send(connection,msg=error,channel=channel)

	def on_quit(self,connection,event):
		user = NickMask(event.source)

		if len(event.arguments)>=1:
			msg = event.arguments[0]
		else:
			msg = ""

		quit_event = signal("quit")
		quit_event.send(connection,msg=msg,nick=user.nick)

	def on_nick(self,connection,event):

		user = NickMask(event.source)

		nick_event = signal("newnick")
		nick_event.send(connection,new=event.target,old=user.nick)

	def on_umode(self,connection,event):

		mode_event = signal("umode")
		mode_event.send(connection,mode=' '.join(event.arguments),who=event.source,target=event.target)

	def on_mode(self,connection,event):

		pmode = irc.modes.parse_channel_modes(' '.join(event.arguments))

		mode_event = signal("mode")
		mode_event.send(connection,mode=pmode,who=event.source,target=event.target)

	def on_nicknameinuse(self,connection,event):
		newnick = connection.get_nickname() + "_"
		connection.nick(newnick)
		nick_event = signal("mynick")
		nick_event.send(connection,nick=newnick)

	def on_welcome(self, connection, event):

		welcome_event = signal("registered")
		welcome_event.send(connection)

		connection.send_items("PROTOCTL","UHNAMES")

		mynick = connection.get_nickname()
		nick_event = signal("mynick")
		nick_event.send(connection,nick=mynick)

	def on_join(self, connection, event):

		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost

		join_event = signal("join")
		join_event.send(connection,channel=event.target,nick=nick,hostmask=hostmask)

	def on_part(self, connection, event):
		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost

		if nick == connection.get_nickname(): return

		if len(event.arguments)>=1:
			msg = event.arguments[0]
		else:
			msg = ""

		part_event = signal("part")
		part_event.send(connection,msg=msg,channel=event.target,nick=nick,hostmask=hostmask)

	def on_privmsg(self, connection, event):
		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost

		target = event.target
		msg = event.arguments[0]

		chat = signal("privmsg")
		chat.send(connection,msg=msg,target=target,nick=nick,hostmask=hostmask)

	def on_pubmsg(self, connection, event):
		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost

		target = event.target
		msg = event.arguments[0]

		chat = signal("pubmsg")
		chat.send(connection,msg=msg,target=target,nick=nick,hostmask=hostmask)

	def on_pubnotice(self,connection,event):
		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost
		target = event.target
		msg = event.arguments[0]

		chat = signal("notice")
		chat.send(connection,msg=msg,target=target,nick=nick,hostmask=hostmask)

	def on_privnotice(self,connection,event):
		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost
		target = event.target
		msg = event.arguments[0]

		if not event.source:
			nick = "SERVER"
			hostmask = "SERVER"

		chat = signal("notice")
		chat.send(connection,msg=msg,target=target,nick=nick,hostmask=hostmask)

	def on_action(self, connection, event):
		user = NickMask(event.source)
		nick = user.nick
		hostmask = user.userhost

		target = event.target
		msg = event.arguments[0]

		chat = signal("action")
		chat.send(connection,msg=msg,target=target,nick=nick,hostmask=hostmask)

	def on_namreply(self,connection,event):
		channel = event.arguments[1]
		users = event.arguments[2].split(' ')
		users = list(filter(None, users))

		nrep = signal("names")
		nrep.send(connection,users=users,channel=channel)

	def on_endofnames(self,connection,event):
		channel = event.arguments[0]
		enrep = signal("endnames")
		enrep.send(connection,channel=channel)

	def on_motdstart(self,connection,event):
		self.motd = []

	def on_motd(self,connection,event):
		line = event.arguments[0]
		self.motd.append(line)

	def on_endofmotd(self,connection,event):
		mrep = signal("motd")
		mrep.send(connection,motd=self.motd)

def build_channel_info(n,chan):

	ci = []

	ci.append(n)

	if chan.has_key():
		ci.append(chan.key)
	else:
		ci.append('')

	if chan.has_limit():
		ci.append(int(chan.modes["l"]))
	else:
		ci.append(0)

	if chan.is_invite_only():
		ci.append(1)
	else:
		ci.append(0)

	if chan.has_allow_external_messages():
		ci.append(1)
	else:
		ci.append(0)

	if chan.has_topic_lock():
		ci.append(1)
	else:
		ci.append(0)

	if chan.is_protected():
		ci.append(1)
	else:
		ci.append(0)

	if chan.is_secret():
		ci.append(1)
	else:
		ci.append(0)

	if chan.is_moderated():
		ci.append(1)
	else:
		ci.append(0)

	if chan.has_mode('c'):
		ci.append(1)
	else:
		ci.append(0)

	return ci