import irc
import dcpu

def onPing(nick, user, host, chan, data):
    irc.command('PONG', data)

irc.on('PING', onPing)

def onAssemble(nick, user, host, chan, matches):
    binary, errors = dcpu.assemble(matches[1])

    if binary:
        irc.privmsg(nick, chan, ', '.join(binary)
    if errors:
        irc.privmsg(nick, chan, errors)

irc.onMatch(">>>(.+)", onAssemble)

def onExecute(nick, user, host, chan, matches):
    executed = dcpu.execute(matches[1])
    privmsg(nick, chan, executed)

def onMsgToMe(nick, chan, msg):
    if re.match("reload.*", msg):
        privmsg(nick, chan, "Reloading in progress")
	parent.reload_now = True
    if re.match("hello.*", msg):
        privmsg(nick, chan, "Howdy!")
    if re.match("(how.*you|sup|what*up)", msg, re.IGNORECASE):
        privmsg(nick, chan, "I'm fine. How about you?")

execute_re = re.compile(">>(.+)")
assemble_re = re.compile(">>>(.+)")

def onPrivMsg(nick, chan, msg):
    parent.last_nick = nick
    parent.last_chan = chan
    print "Message from " + nick + " to " + chan + ": " + msg
    to_me_match = re.match("^" + config.nick + "[^ ]? (.+)", msg)
    assemble_match = assemble_re.match(msg)
    execute_match = execute_re.match(msg)

    if assemble_match:
        assembled = dcpu.assemble(assemble_match.group(1))
	if assembled[0] != "":
	    privmsg(nick, chan, ', '.join(assembled[0]))
	if assembled[1] != "":
            privmsg(nick, chan, assembled[1])
    elif execute_match:
        executed = dcpu.execute(execute_match.group(1))
        privmsg(nick, chan, executed)
    elif to_me_match or chan == config.nick:
        if to_me_match: msg = to_me_match.group(1)
        onMsgToMe(nick, chan, msg)