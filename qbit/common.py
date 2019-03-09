
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
import platform
import json
import re

# Globally load in bundled images
globals()["qbit.resources"] = __import__("qbit.resources")

import qbit.colour

APPLICATION_NAME = "Qbit"
APPLICATION_VERSION = "0.0022"
APPLICATION_DESCRIPTION = "IRC Micro-Client"

HOST_OS = platform.system()
HOST_OS_VERSION = platform.release()
HOST_PLATFORM = platform.platform(aliased=1)

DEFAULT_IRC_NICKNAME = "qbit"
DEFAULT_IRC_USERNAME = "qbit"
DEFAULT_IRC_IRCNAME = f"Qbit {APPLICATION_VERSION}"

INSTALL_DIRECTORY = sys.path[0]
QBIT_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "qbit")
IMAGE_SPINNER = os.path.join(QBIT_DIRECTORY, "spinner.gif")

INITIAL_WINDOW_WIDTH = 500
INITIAL_WINDOW_HEIGHT = 300

INSTALL_DIRECTORY = sys.path[0]
QBIT_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "qbit")
CONFIG_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "config")

DISPLAY_CONFIGURATION = os.path.join(CONFIG_DIRECTORY, "display.json")
LAST_SERVER_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "lastserver.json")
AUTOJOIN_FILE = os.path.join(CONFIG_DIRECTORY, "autojoin.json")

USER_FILE = os.path.join(CONFIG_DIRECTORY, "user.json")

IMAGE_QBIT_ICON = ":/qbit.png"
IMAGE_PAGE_ICON = ":/page.png"
IMAGE_EXIT_ICON = ":/exit.png"
IMAGE_RESTART_ICON = ":/restart.png"
IMAGE_CHANNEL_ICON = ":/channel.png"
IMAGE_USER_ICON = ":/user.png"
IMAGE_CLEAR_ICON = ":/clear.png"
IMAGE_SERVER_ICON = ":/server.png"
IMAGE_ABOUT_ICON = ":/about.png"
IMAGE_PLUS_ICON = ":/plus.png"
IMAGE_MINUS_ICON = ":/minus.png"
IMAGE_CLIPBOARD_ICON = ":/clipboard.png"
IMAGE_NO_ICON = ":/no.png"
IMAGE_UNIGNORE_ICON = ":/unignore.png"
IMAGE_X_ICON = ":/x.png"

IMAGE_LOGO = ":/logo.png"
IMAGE_PYTHON = ":/python.png"
IMAGE_QT = ":/qt.png"
IMAGE_GPL = ":/gpl.png"

# Set display defaults
QBIT_FONT = "Consolas"

NORMAL_FONT_SIZE = 10
BIG_FONT_SIZE = 12
SMALL_FONT_SIZE = 8

LINK_URLS = True

TEXT_BACKGROUND_COLOR = "#ffffff"
TEXT_COLOR = "#000000"
ERROR_COLOR = "#FF0000"
SYSTEM_COLOR = "#FF9C00"
SELF_COLOR = "#FF0000"
USERNAME_COLOR = "#00007F"
ACTION_COLOR = "#009300"
LINK_COLOR = "#00007F"
NOTICE_COLOR = "#9C009C"
MOTD_COLOR = "#00007F"
ERROR_COLOR = "#FF0000"

GRADIENT_LIGHTEN = 0.95

MAX_USERNAME_SIZE = 16

CHANNEL_INFO_NAME = 0
CHANNEL_INFO_KEY = 1
CHANNEL_INFO_LIMIT = 2
CHANNEL_INFO_INVITEONLY = 3
CHANNEL_INFO_ALLOWEXTERNAL = 4
CHANNEL_INFO_TOPICLOCKED = 5
CHANNEL_INFO_PROTECTED = 6
CHANNEL_INFO_SECRET = 7
CHANNEL_INFO_MODERATED = 8
CHANNEL_INFO_NOCOLORS = 9

def is_integer(n):
	try:
		int(n)
	except ValueError:
		return False
	return True

def save_display_config(config):
	with open(DISPLAY_CONFIGURATION, "w") as write_data:
		json.dump(config, write_data)

def loadDisplayConfig():
	if os.path.isfile(DISPLAY_CONFIGURATION):
		with open(DISPLAY_CONFIGURATION, "r") as read_data:
			data = json.load(read_data)
			return data
	else:
		dc = {
			"font": QBIT_FONT,
			"fontsize": NORMAL_FONT_SIZE,
			"fontbig": BIG_FONT_SIZE,
			"fontsmall": SMALL_FONT_SIZE,
			"background": TEXT_BACKGROUND_COLOR,
			"text": TEXT_COLOR,
			"error": ERROR_COLOR,
			"system": SYSTEM_COLOR,
			"self": SELF_COLOR,
			"user": USERNAME_COLOR,
			"action": ACTION_COLOR,
			"link": LINK_COLOR,
			"notice": NOTICE_COLOR,
			"motd": MOTD_COLOR,
			"links": LINK_URLS
		}
		with open(DISPLAY_CONFIGURATION, "w") as write_data:
			json.dump(dc, write_data)
		return dc

# Load in display settings from file
DC = loadDisplayConfig()
QBIT_FONT = DC["font"]
NORMAL_FONT_SIZE = DC["fontsize"]
BIG_FONT_SIZE = DC["fontbig"]
SMALL_FONT_SIZE = DC["fontsmall"]
TEXT_BACKGROUND_COLOR = DC["background"]
TEXT_COLOR = DC["text"]
ERROR_COLOR = DC["error"]
SYSTEM_COLOR = DC["system"]
SELF_COLOR = DC["self"]
USERNAME_COLOR = DC["user"]
ACTION_COLOR = DC["action"]
LINK_COLOR = DC["link"]
NOTICE_COLOR = DC["notice"]
MOTD_COLOR = DC["motd"]
LINK_URLS = DC["links"]

CHAT_TEMPLATE = f"""
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="text-align: right; vertical-align: top; !GRADIENT!"><font color="!COLOR!">!USER!</font></td>
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";">&nbsp;</td>
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";"><font color="!CCHAT!">!MESSAGE!</font></td>
	</tr>
  </tbody>
</table>
"""

ACTION_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="text-align: left; vertical-align: top; !GRADIENT!"><font color="!COLOR!"><b>!USER!</b> !MESSAGE!</font></td>
	</tr>
  </tbody>
</table>
"""

SYSTEM_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";"><font color="!COLOR!">!MESSAGE!</font></td>
	</tr>
  </tbody>
</table>
"""

def inject_www_links(txt):
	if not LINK_URLS: return txt
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)
	for u in urls:
		u = re.sub('<[^<]+?>', '', u)
		link = f"<a href=\"{u}\"><span style=\"text-decoration: underline; font-weight: bold; color: {LINK_COLOR}\">{u}</span></a>"
		txt = txt.replace(u,link)
	return txt

def pad_nick(nick,size):
	x = size - len(nick)
	if x<0 : x = 0
	y = '&nbsp;'*x
	return f"{y}{nick}"

def system_display(text):
	msg = SYSTEM_TEMPLATE.replace('!COLOR!',SYSTEM_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	return msg

def error_display(text):
	msg = SYSTEM_TEMPLATE.replace('!COLOR!',ERROR_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	return msg

def chat_display(user,text,max):
	text = remove_html_markup(text)
	user = pad_nick(user,max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',USERNAME_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = qbit.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = qbit.colour.Color(USERNAME_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def mychat_display(user,text,max):
	text = remove_html_markup(text)
	user = pad_nick(user,max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',SELF_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = qbit.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = qbit.colour.Color(SELF_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def action_display(user,text):
	text = remove_html_markup(text)
	text = inject_www_links(text)
	msg = ACTION_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',ACTION_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = qbit.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = qbit.colour.Color(ACTION_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def notice_display(user,text,max):
	text = remove_html_markup(text)
	user = pad_nick(user,max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',NOTICE_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = qbit.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = qbit.colour.Color(NOTICE_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def motd_display(text,max):
	user = pad_nick("MOTD",max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',MOTD_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = qbit.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = qbit.colour.Color(MOTD_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c

    return out

def save_last_server(host,port,password,ssl):
	sinfo = {
			"host": host,
			"port": port,
			"password": password,
			"ssl": ssl
		}
	with open(LAST_SERVER_INFORMATION_FILE, "w") as write_data:
		json.dump(sinfo, write_data)

def get_last_server():
	if os.path.isfile(LAST_SERVER_INFORMATION_FILE):
		with open(LAST_SERVER_INFORMATION_FILE, "r") as read_server:
			data = json.load(read_server)
			return data
	else:
		si = {
			"host": '',
			"port": '',
			"password": '',
			"ssl": False
		}
		return si

def save_autojoin_channels(chans):
	with open(AUTOJOIN_FILE, "w") as write_data:
		json.dump(chans, write_data)

def get_autojoins():
	if os.path.isfile(AUTOJOIN_FILE):
		with open(AUTOJOIN_FILE, "r") as read_server:
			data = json.load(read_server)
			return data
	else:
		return []

def get_user():
	if os.path.isfile(USER_FILE):
		with open(USER_FILE, "r") as read_user:
			data = json.load(read_user)
			return data
	else:
		si = {
			"nick": DEFAULT_IRC_NICKNAME,
			"username": DEFAULT_IRC_USERNAME,
			"realname": DEFAULT_IRC_IRCNAME
		}
		return si

def save_user(user):
	with open(USER_FILE, "w") as write_data:
		json.dump(user, write_data)
