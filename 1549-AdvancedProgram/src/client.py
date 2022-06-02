# Libraries import
import socket
import threading
import os
import sqlite3
from ipaddress import IPv4Network

db = sqlite3.connect("Database.db", check_same_thread=False)
cursor = db.cursor()

with open('temp_ip.txt', 'w') as x:
    x.write("127.0.0.1")
with open('temp_port.txt', 'w') as z:
    z.write("80")


def login():
    login_boolean = False

    while True:
        global username, password

        username = input("UUID:")
        password = input("Password:")
        # A query to check user details within the database to match the login and allow access to the application
        query = "SELECT * FROM details WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003' AND PASSWORD = '{}' AND ID".format(
            username, password)

        cursor.execute(query)
        rows = cursor.fetchall()
        # If the data entered is a match against the list then we change the boolean to true and allow login
        if len(rows) == 1:
            login_boolean = True
        if login_boolean:
            # Runs the main server script
            os.startfile("server.py")
            main()
            user_temp = open("temp_user.txt", "w")
            user_temp.write(username)
            user_temp.close()
            break
        else:
            print("Login error", "Incorrect Username/Password")

def main():
    global username, password

    # Takes the username from the user login and displays that as the 'nickname'
    nickname = input("Choose your nickname: ")
    print(30 * "-")
    print("Use #help to get commands")
    print(30 * "-")
    # IP runs through temp file to get to designated addresses
    host = "127.0.0.1"
    # Designated  port
    port = 80

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
                    print("     #cg  - Create group")
                    print("     #gau - Group Add User")
                    print("     #gru - Group Remove User")
                    print("     #gl  - Group List")
                    print("     #ctg - Connect to group")
                    print("\n")
                elif get_message == '#cg':
                    print("Creating Group")
                    create_group()
                elif get_message == '#gau':
                    print("Group Add User")
                    group_add_user()
                elif get_message == '#gru':
                    print("Group Remove User")
                    group_remove_user()
                elif get_message == '#gl':
                    print("Group List")
                    group_list()
                elif get_message == '#ctg':
                    print("Connecting to group")
                    os.startfile("connect_client.py")
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


def create_group():
    global username
    while True:
        # Runs a check on the user input if they wish to exit or carry on with the procedure
        group_name = input("Enter Group Name: ")
        group_name_check = group_name.upper()
        # Query runs through the groups within the database and gathers the data
        query1 = "SELECT GROUPS FROM addresses WHERE GROUPS = '{}'".format(group_name_check)
        cursor.execute(query1)
        rows = cursor.fetchall()
        # check within the fetched data to check if the inputted group name matches anything within the database
        if rows:
            print("Group name already exists, enter a different name")
            # Display of group name existing, then carrys on with user inputs.
            continue
        else:
            # Server will increment from what is there by order of 127.0.0.2-127.255.255.254
            network = IPv4Network('127.0.0.0/8')

            reserved = []
            # Takes all the ip's that are within the database and allows for them to be checked and incremented
            # for the next ip to be used.
            query2 = "SELECT IP FROM addresses"
            cursor.execute(query2)
            rows = cursor.fetchall()
            # Gathers all the data individually from the nested list rows and gets it into a one dimension list
            for row in rows:
                for i in row:
                    reserved.append(i)
            # Check method using the library ipaddress to simply iterate to the next needed ip
            hosts_iterator = (host for host in network.hosts() if str(host) not in reserved)
            # Gets the next ip needed and appends it for writing to the database
            store_next_ip = next(hosts_iterator)
            reserved.append(store_next_ip)
            # Query that takes the users username and INSERTS into the database table where all the ip addresses of\
            # individual users are stored
            add_query = "INSERT INTO addresses('UUID', 'IP', 'PORT', 'ADMIN', 'GROUPS') VALUES ('{}-8c10-11eb-8dcd-0242ac130003', '{}', '{}', '{}', '{}')".format(
                username, store_next_ip, 80, 1, group_name_check)
            cursor.execute(add_query)
            db.commit()
            print("Server", group_name_check,"has been created, the ip to your server is ", store_next_ip)
            break


def group_add_user():
    global username

    check_ip = []
    # Gets the group name from the specific IP and adds the data to database
    group_name_add = ''
    # Query checks all the IP's that the user is admin of
    query = "SELECT IP FROM addresses WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003' AND ADMIN = 1 ".format(username)
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        for i in row:
            check_ip.append(i)
    # Query gets all user ID's for when the user enters the details of the other users
    check_uuid = "SELECT UUID FROM details"
    cursor.execute(check_uuid)
    check_rows = cursor.fetchall()

    check_rows_list = []

    for row in check_rows:
        for r in row:
            check_rows_list.append(r)
    # If the user is not admin of any server, a message is displayed and they are taken back to the main menu
    if not check_ip:
        print("You are not Admin of any server, therefore, cannot add users")
        return
    # Displays all the IP's the user can add other users to
    print("IP List")
    for i in check_ip:
        print(i)
    while True: #
        select_ip = input("Select IP:")
        # IP check against the list avaiable to the user so they cannot add users to any IP's they dont have admin of
        if select_ip not in check_ip:
            print("Invalid IP, Enter again")
            continue
        else:
            group_get = "SELECT GROUPS FROM addresses WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003' AND IP = '{}' ".format(
                username, select_ip)
            cursor.execute(group_get)
            check_groups = cursor.fetchall()
            for row in check_groups:
                for i in row:
                    group_name_add = i

            # Once the IP is selected the user can address what user they want to add to the database
            user_add = input("Users UUID:")
            # Checker against the ID's and returns invalid UUID if that user does not exist
            if (user_add + "-8c10-11eb-8dcd-0242ac130003") not in check_rows_list:
                print("Invalid UUID, Enter again")
                continue
            else:
                # From the data entered this query checks if the user already exists within that specific server
                check_uuid_in_server_query = "SELECT UUID FROM addresses WHERE IP = '{}' AND UUID = '{}-8c10-11eb-8dcd-0242ac130003'".format(select_ip, user_add)
                cursor.execute(check_uuid_in_server_query)
                check_uuid_in_server_exe = cursor.fetchall()
                # If user is present in the query then conditions break off back to the menu
                if check_uuid_in_server_exe:
                    print("User already in server")
                    break
                else:
                    # Query inserts the data into the database using the format of the tables, and sets the value of the users ADMIN role to 0
                    query = "INSERT INTO addresses('UUID', 'IP', 'PORT', 'ADMIN', 'GROUPS') VALUES ('{}-8c10-11eb-8dcd-0242ac130003', '{}', '{}', '{}', '{}')".format(
                        user_add, select_ip, 80, 0, group_name_add)
                    cursor.execute(query)
                    db.commit()
                    print("User has been added to server ", select_ip)
                    break


def group_remove_user():
    check_ip = []
    get_users = []
    goBack = 0
# Query gathers all the IP's that the connected user is capable(Has ADMIN) of deleting from
    query = "SELECT IP FROM addresses WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003' AND ADMIN = 1 ".format(
        username)
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        for i in row:
            check_ip.append(i)
 # If the user is not an admin on any server,they will be prompted
    if not check_ip:
        print("You are not Admin of any server, therefore, cannot remove users")
        return
#Displays all available IP's
    print("IP List")
    for i in check_ip:
        print(i)
    while True:
        select_ip = input("Select IP:")
        if select_ip not in check_ip:
            print("Invalid IP, Enter again")
            continue
        else:
            # Once the selected IP is chosen, the User ID of that IP are now to be displayed
            query = "SELECT UUID FROM addresses WHERE IP = '{}'".format(select_ip)
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                for i in row:
                    get_users.append(i)
            # Display of users allocated in the particular IP 
            print("\nUsers for server IP", select_ip, ":")
            for i in get_users:
                print(i[0:8])

            user_remove = input("Users UUID:")
            if goBack == 1:
                break
            if (user_remove + "-8c10-11eb-8dcd-0242ac130003") not in get_users:
                print("Invalid UUID, Enter again")
                continue
            else: # Simple delete query where the UUID is matched to the users request
                query = "DELETE FROM addresses WHERE UUID = '{}'".format(
                    user_remove + "-8c10-11eb-8dcd-0242ac130003")
                cursor.execute(query)
                db.commit()
                print("User has been removed from server", select_ip)
                break

def group_list():
    server_data = []
    ip_list = []
 # Query gathers all the IP's the connected user can connect to,who has admin rights of and where they were added on selcted IP's
    query = "SELECT IP FROM addresses WHERE UUID = '{}-8c10-11eb-8dcd-0242ac130003'".format(username)
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        for item in row:
            ip_list.append(item)
    # For each IP within the list we are gathering all the data from the users within that IP
    for i in ip_list:
        query = "SELECT GROUPS, IP, ADMIN, UUID FROM addresses WHERE IP = '{}'".format(i)
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            for item in row:
                # Syntax of ID's are unique
                item = item.replace("-8c10-11eb-8dcd-0242ac130003", "")
                server_data.append(item)
    """
    server_data holds all the information related to the user to display on the CLI.
    Admin uses 1's and normal users are 0's. 

    enumerate will loop through all the server_data from nested list to nested list and wherever the conditions apply
    where if '1' then will change to 'Admin' and same for '0' to 'User'
    
    """
    for n, i in enumerate(server_data):
        if i == '1':
            server_data[n] = 'Admin'
        if i == '0':
            server_data[n] = 'User'
    for x in range(0, len(server_data), 4):
        print(server_data[x], server_data[x + 1], server_data[x + 2], server_data[x + 3])


if __name__ == '__main__':
    login()
