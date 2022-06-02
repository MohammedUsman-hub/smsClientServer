# Libraries import
import socket
import threading
import sqlite3
import os

with open('temp_user.txt', 'r') as y:
    username = y.read()

check_ip = []

# source code for this: https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
db = sqlite3.connect("Database.db", check_same_thread=False)
cursor = db.cursor()

query = "SELECT IP FROM addresses WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003'".format(username)
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    for i in row:
        check_ip.append(i)
#Checks that the user inputs the correct Ip address for the server
print("IP List")
for i in check_ip:
    print(i)
while True:
    host = input("Select IP:")
    if host not in check_ip:
        print("Invalid IP, Enter again")
        continue
    else:
        port = int(input("Select PORT:"))
        if host not in check_ip:
            print("Invalid IP, Enter again")
            continue
        else:
            nickname = input("Choose your nickname: ")

            with open('temp_ip.txt', 'w') as x:
                x.write(host)
            with open('temp_port.txt', 'w') as z:
                port_write = str(port)
                z.write(port_write)

            os.startfile("server.py")

            user_check_list = []
            users_in_server = []
            # Once the user connects to the server their details are put in a temp file to give admin privileges depending on if someone is already connected or not
            with open('temp_user.txt', 'r') as y:
                users_in_server = [line.strip() for line in y]
            # Query takes the users ID and checks against the IP they are connecting to and checks if they have admin or not
            query = "SELECT UUID FROM addresses WHERE IP = '{}' AND ADMIN = 1".format(host)
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                for i in row:
                    user_check_list.append(i)
            # If the user is not an admin of that server then they will be given Admin and others removed
            if user_check_list[0] != (username + '-8c10-11eb-8dcd-0242ac130003'):
                # Query updates the table and sets all other users to non-admin, other than the User on the menu
                query3 = "UPDATE addresses SET ADMIN = 0 WHERE IP = '{}'".format(host)
                cursor.execute(query3)
                # Query updates the table just as the one above but gives the user who is connecting to the server admin rights and only occurs on the IP they are connecting to
                query2 = "UPDATE addresses SET ADMIN = 1 WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003' AND IP = '{}'".format(username, host)
                cursor.execute(query2)
                db.commit()
            break



# socket initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connecting client to server
client.connect((host, port))


def receive():
    # making valid connection
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICKNAME':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        # case on wrong ip/port details
        except:
            print("An error occurred!")
            client.close()
            break


def write():
    # message layout
    while True:
        try:
            get_message = input('')
            if get_message == '#help':
                print("\n")
                print("     #exit - Exit client or use CRTL + C")
                print("\n")
            else:
                message = '{}: {}'.format(nickname, get_message)
                client.send(message.encode('ascii'))
        except EOFError:
            client.close()
            exit()


# receiving multiple messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()
# sending messages
write_thread = threading.Thread(target=write)
write_thread.start()
