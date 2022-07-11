#   Author: Omer Dayan - 312409386
#   11/11/2021

import socket
import protocol

IP = "127.0.0.1"
SAVED_PHOTO_LOCATION = r'C:\networks\work\photo.jpg'  # The path + filename where the copy
# of the screenshot at the client should be saved


def handle_server_response(my_socket, cmd):
    """
    Receive the response from the server and handle it, according to the request
    For example, DIR should result in printing the contents to the screen,
    Note- special attention should be given to SEND_PHOTO as it requires and extra receive
    """
    # (8) treat all responses except SEND_PHOTO
    if cmd == 'EXIT':
        return 'EXIT'

    if cmd != 'SEND_PHOTO':
        length = my_socket.recv(4).decode()
        response = my_socket.recv(int(length)).decode()
        return response

    # (10) treat SEND_PHOTO
    if cmd == 'SEND_PHOTO':
        length = int(my_socket.recv(4).decode())  # מספר הספרות
        length = my_socket.recv(length).decode()  # הספרות עצמן
        photo = open(SAVED_PHOTO_LOCATION, 'wb')
        photo.write(my_socket.recv(int(length)))
        photo.close()
        return 'OK'


def main():
    # open socket with the server

    # (2)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, 8820))

    # print instructions
    print('Welcome to remote computer application. Available commands are:\n')
    print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')
    # loop until user requested to exit
    while True:
        cmd = input("Please enter command:\n")

        # When TAKE_SCREENSHOT is entered, we will attach the path.
        if cmd == 'TAKE_SCREENSHOT':
            cmd = cmd + ' ' + SAVED_PHOTO_LOCATION

        # Sent to the input integrity check function, and sent to the server
        if protocol.check_cmd(cmd):
            command = cmd.split()
            packet = protocol.create_msg(cmd)
            my_socket.send(packet.encode())

            # Will receive the server response
            response = handle_server_response(my_socket, command[0])

            # When EXIT is entered, we will exit.
            if command[0] == 'EXIT':
                break
            print(response)

        else:
            print("Not a valid command, or missing parameters\n")

    my_socket.close()


if __name__ == '__main__':
    main()
