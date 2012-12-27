import socket
import re
import threading
import sys

command_handlers = []
privmsg_handlers = []
msgtome_handlers = []

def command(command, params):
    print "Command: (\"" + command + "\", \"" + params + ")"
    msg = command + " " + params
    print msg
    server.sendall(msg + "\r\n")

def privmsg(nickIn, chan, msg):

    lines = msg.split("\n")
    if len(lines) > 1:
        for line in lines:
            privmsg(nickIn, chan, line)
    elif msg != "":
        response = ""

        if chan == nick:
            response += nickIn + " :" + msg
        else:
            response += chan + " :" + nickIn + ": " + msg

        command("PRIVMSG", response)

def handlePing(nick, user, host, chan, params):
    print params
    command('PONG', params)

def handleMsgToMe(nick, user, host, chan, params):
    for regex, callback in msgtome_handlers:
        matches = regex.match(params)
        if matches:
            callback(nick, user, host, chan, params)

def handlePrivmsg(nickIn, user, host, chan, params):
    for regex, callback in privmsg_handlers:
        matches = regex.match(params)
        if matches:
            callback(nickIn, user, host, chan, matches)
            
    global nick
    matches = re.match("^" + nick + "[:, ]?(.*)", params)
    if matches:
        handleMsgToMe(nickIn, user, host, chan, matches.group(1))

class EventHandler(threading.Thread):
    def run(self):
        while True:
            try:
                message = server.recv(4096)
                if message == '':
                    server.close()

                handleCommand(message)
            except Exception as e:
               print e.message

def connect(host, port, nickIn="TestBot", password="", name="dcpubot", realname="DCPU Bot"):
    global nick
    nick = nickIn
    
    global server
    server = socket.create_connection((host, port))

    server.sendall("PASS " + password + "\r\n")
    server.sendall("NICK " + nick + "\r\n")
    server.sendall("USER " + name + " 0 * :" + realname + "\r\n")

    onCommand('PING', handlePing)
    onCommand('PRIVMSG', handlePrivmsg)

    eventHandler = EventHandler()
    eventHandler.start()

def join(channels):
    print channels
    if type(channels) is str:
        print "JOIN " + channels
        server.sendall("JOIN " + channels + "\r\n")
    else:
        for channel in channels:
            print "JOIN " + channel
            server.sendall("JOIN " + channel + "\r\n")

message_re = re.compile("^((:([^!@ ]+)(!([^@ ]+))?(@([^ ]+))? ?)?([^ ]+)?)? ?((?!:)[^ ]*)[^:]*(:(.*))?")

def handleCommand(message):
    print "Message: " + message
    message_data = message_re.match(message)

    if message_data:
    
        nick = message_data.group(3)
        user = message_data.group(5)
        host = message_data.group(7)
        command = message_data.group(8)
        chan = message_data.group(9)
        params = message_data.group(11)
    
        for com, callback in command_handlers:
            if com == command:
                callback(nick, user, host, chan, params)
    else:
        print "Message could not be parsed: " + message

def onCommand(command, callback):
    global command_handlers
    command_handlers.append((command, callback))

def onPrivmsg(reg, callback):
    global privmsg_handlers
    regex = re.compile(reg)
    privmsg_handlers.append((regex, callback))

def onMsgToMe(reg, callback):
    global msgtome_handlers
    regex = re.compile(reg)
    msgtome_handlers.append((regex, callback))
