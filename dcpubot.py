import socket
import config
import irc
import sys

server = socket.create_connection((config.host, config.port))

server.sendall("PASS " + config.password + "\r\n")
server.sendall("NICK " + config.nick + "\r\n")
server.sendall("USER dcpubot 0 * :DCPU Bot\r\n")

for chan in config.chan:
    server.sendall("JOIN " + chan + "\r\n")

def irc_load():
    print "Reloading IRC module"
    global irc
    irc = reload(irc)
    irc.init(server, config, sys.modules[__name__])

irc_load()
print "Done loading."

reload_now = False
last_nick = ""
last_chan = ""

while 1:
    try:
        message = server.recv(4096)
        if message == '':
            server.close()
            break

        irc.onData(message)
    except Exception as e:
      irc.privmsg(last_nick, last_chan, "Now look at that. An error just happened. How cute. Error: " + e.message)
    if reload_now:
      irc_load()
      irc.privmsg(last_nick, last_chan, "Reloading finished")
      reload_now = False
