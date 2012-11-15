import socket
import config
import irc
import sys

server = socket.create_connection((config.host, config.port))

server.sendall("PASS " + config.password + "\r\n")
server.sendall("NICK " + config.nick + "\r\n")
server.sendall("USER dcpubot 0 * :DCPU Bot\r\n")
server.sendall("JOIN " + config.chan + "\r\n")

def irc_load():
    print "Reloading IRC module"
    global irc
    irc = reload(irc)
    irc.init(server, config, sys.modules[__name__])

irc_load()
print "Done loading."

reload_now = False

while 1:
    try:
        message = server.recv(4096)
        if message == '':
            server.close()
            break

        irc.onData(message)
    except Exception as e:
      irc.privmsg('', config.chan, "Now look at that. An error just happened. How cute. Error: " + e.message)
    if reload_now:
      irc_load()
      irc.privmsg('', config.chan, "Reloading finished")
      reload_now = False
