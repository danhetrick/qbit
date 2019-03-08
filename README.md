![Qbit](https://github.com/danhetrick/qbit/blob/master/resources/logo.png)

# Qbit
A GUI IRC client written in Python and Qt5.

# Installation
Make sure the requirements are installed first. To use **Qbit**, you'll need to have Qt5 and a few Python libraries. You can use `pip` to install everything:

    pip install PyQt5
    pip install irc
    pip install blinker

To connect to IRC via SSL, some more libraries are needed:

    pip install pyOpenSSL
    pip install service_identity

# Another IRC client?
Yes! I've been using IRC for almost 20 years, and I've never found a client that I'm completely comfortable with. I've used everything from ircii and Irssi to mIRC and HexChat, and never really felt "at home" with a specific client. So I decided to write my own! **Qbit** is what I like to call a "micro-client".

# What's a "micro-client"?

**Qbit** uses a single window (mostly), and only displays information for what you're working with, when you're working with it. So, if you're chatting in a channel, **Qbit** only displays that channel and what's going on in there. If you're privately chatting with a user, **Qbit** only displays that chat session.  These different displays are called "pages", and **Qbit** can handle as many pages as you want. A fresh page is created every time you join a channel or receive a private message; you can switch between pages using the "page selector":

![Qbit Interface](https://github.com/danhetrick/qbit/blob/master/ui_guide.png)

Every page features a *chat display* and a *text entry*; only IRC channel pages feature a *user display*. Read incoming chat messages in the *chat display*, and enter text into the *text entry* to send messages. On a channel page, the *text entry* will send messages to the appropriate channel, and on a private message page, the *text entry* will send messages to the person you're chatting with. The *page selector* will show the name of the channel or user you're chatting with on that page.

If a page you're not currently viewing has received chat messages, that will be displayed in the "Unread Messages" menu; every page that has messages that haven't been viewed will be added to that menu. Switch to the appropriate page via the *page selector* or the "Unread Messages" menu to view the unread messages. Alternately, you can use the keyboard shortcut *Ctrl+U* to set all unread messages as "read" (which also clears the "Unread Messages" menu).