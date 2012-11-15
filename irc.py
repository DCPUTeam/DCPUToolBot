import re
import assembler

def init(serv, conf, par):
    print "IRC is initializing..."
    global server
    global config
    global parent
    global assembler
    server = serv
    config = conf
    parent = par
    assembler = reload(assembler)


def send(msg):
    print msg
    server.send(msg + "\r\n")

def privmsg(nick, chan, msg):
    parent.last_nick = nick
    parent.last_chan = chan

    response = "PRIVMSG "

    if chan == config.nick:
        response += nick + " :" + msg
    else:
        response += chan + " :" + nick + ": " + msg

    send(response)

def onMsgToMe(nick, chan, msg):
    if re.match("reload.*", msg):
        privmsg(nick, chan, "Reloading in progress")
	parent.reload_now = True
    if re.match("hello.*", msg):
        privmsg(nick, chan, "Howdy!")
    if re.match("(how.*you|sup|what*up)", msg):
        privmsg(nick, chan, "I'm fine. How about you?")

assemble_re = re.compile(">>>(.+)")

def onPrivMsg(nick, chan, msg):
    print "Message from " + nick + " to " + chan + ": " + msg
    to_me_match = re.match("^" + config.nick + "[^ ]? (.+)", msg)
    assemble_match = assemble_re.match(msg)

    if assemble_match:
        assembled = assembler.assemble(assemble_match.group(1))
	if assembled[1] != "":
            privmsg(nick, chan, assembled[1])
	else:
	    privmsg(nick, chan, ', '.join(assembled[0]))
    elif to_me_match or chan == config.nick:
        if to_me_match: msg = to_me_match.group(1)
        onMsgToMe(nick, chan, msg)

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
        onPrivMsg(privmsg_match.group(1), privmsg_match.group(2), privmsg_match.group(3))
