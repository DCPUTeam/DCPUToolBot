import socket
import config
import irc

server = socket.create_connection((config.host, config.port))

server.sendall("PASS " + config.password + "\r\n")
server.sendall("NICK " + config.nick + "\r\n")
server.sendall("USER dcpubot 0 * :DCPU Bot\r\n")
server.sendall("JOIN " + config.chan + "\r\n")

def irc_load():
    global irc
    irc = reload(irc)
    irc.init(server, config)

irc_load()

while 1:
    message = server.recv(4096)
    if message == '':
        server.close()
        break

    else:
        if irc.onData(message) == 'reload':
            irc_load()
