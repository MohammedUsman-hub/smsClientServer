# Libraries import
import socket
import threading
import datetime
from time import sleep

# IP runs through temp file to get to designated addresses
with open('temp_ip.txt', 'r') as x:
    host = x.read()
# Designated  port
with open('temp_port.txt', 'r') as y:
    port_read = y.read()
    port = int(port_read) 
# socket initialization
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binding host and port to socket
server.bind((host, port)) #this method binds the host and port to socket
server.listen() #This method starts the TCP listener 

clients = []
nicknames = []

def gettime():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

# broadcast function declaration
def broadcast(message):
    for client in clients:
        get_message = message.decode('ascii')
        client.send('<<{}>> {}'.format(gettime(), get_message).encode('ascii'))


def handle(client):
    while True:
        # receiving valid messages from client
        try:
            message = client.recv(1024)
            broadcast(message)
        # removing clients
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()#This method closes a removed clients socket thus disconnecting them
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break


# accepting multiple clients
def receive():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        client.send('NICKNAME'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
