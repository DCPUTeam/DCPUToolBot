import re

server = None
config = None

def init(serv, conf):
    global server
    global config
    server = serv
    config = conf


def send(msg):
    print msg
    server.send(msg + "\r\n")

def privmsg(nick, chan, msg):
    response = "PRIVMSG "

    if chan == config.nick:
        response += nick + " :" + msg
    else:
        response += chan + " :" + nick + ": " + msg

    send(response)

def onMsgToMe(nick, chan, msg):
    privmsg(nick, chan, msg)
    if msg == "reload":
        return 'reload'


def onPrivMsg(nick, chan, msg):
    print "Message from " + nick + " to " + chan + ": " + msg
    to_me_match = re.match("^" + config.nick + "[^ ]? (.+)", msg)

    if to_me_match or chan == config.nick:
        if to_me_match: msg = to_me_match.group(1)
        return onMsgToMe(nick, chan, msg)

ping_re = re.compile("^PING :(.*)")
privmsg_re = re.compile("^:([^!@]+).+PRIVMSG ([^ ]+) :(.*)")

def onData(data):
    print(data)

    ping_match = ping_re.match(data)
    privmsg_match = privmsg_re.match(data)

    if ping_match:
        response = "PONG :" + ping_match.group(1)
        send(response)
    elif privmsg_match:
        return onPrivMsg(privmsg_match.group(1), privmsg_match.group(2), privmsg_match.group(3))
