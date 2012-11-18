#!/usr/bin/env python
import irc
import config
import dcpu

irc.connect(config.host, config.port, config.nick, config.password)
irc.join(config.chan)

def onAssemble(nick, user, host, chan, matches):
    print "Assembling"
    print matches.group()
    print matches.group(1)
    binary, errors = dcpu.assemble(matches.group(1))

    if binary:
        irc.privmsg(nick, chan, ', '.join(binary))
    if errors:
        irc.privmsg(nick, chan, errors)

irc.onPrivmsg(">>>(.+)", onAssemble)

def onExecute(nick, user, host, chan, matches):
    executed, errors = dcpu.execute(matches.group(1))

    if executed:
        irc.privmsg(nick, chan, executed)
    if errors:
        irc.privmsg(nick, chan, errors)

irc.onPrivmsg(">>([^>].+)", onExecute)

def onHello(nick, user, host, chan, matches):
    irc.privmsg(nick, chan, "Howdy!")

irc.onMsgToMe(".*hello.*", onHello)

def onSup(nick, user, host, chan, matches):
    irc.privmsg(nick, chan, "I'm fine. How about you?")

irc.onMsgToMe(".*(how.*you|sup|what.*up).*", onSup)
