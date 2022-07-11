#   Author: Omer Dayan - 312409386
#   11/11/2021

import socket
import protocol
import os
import glob
import shutil
import subprocess
import pyautogui






IP = "0.0.0.0"
PHOTO_PATH = r'c:\networks\photo.jpg'  # The path + filename where the screenshot at the server should be saved
# המיקום של התמונה
LENGTH_FIELD_SIZE = 4


def check_client_request(cmd):
    """
    Break cmd to command and parameters.
    Check if the command and params are good.

    For example, the filename to be copied actually exists

    Returns:
        valid: True/False
        command: The requested cmd (ex. "DIR")
        params: List of the cmd params (ex. ["c:\\cyber"])
    """
    # Use protocol.check_cmd first

    if protocol.check_cmd(cmd) is False:
        return False, None, None

    if cmd == 'EXIT':
        return False, None, None

    if cmd == 'SEND_PHOTO':
        if os.path.isfile(PHOTO_PATH):
            return True, cmd, PHOTO_PATH
        return False, None, None

    # Then make sure the params are valid
    out = True
    cmd = cmd.split()
    name = cmd[0]
    path = cmd[1]

    if name == 'TAKE_SCREENSHOT':
        out = os.path.basename(path)

    if name == 'DIR':
        out = os.path.basename(path)

    if name == 'DELETE':
        if os.path.isfile(path):
            out = True
        else:
            out = False

    if name == 'EXECUTE':
        out = os.path.isfile(path)

    if cmd[0] == 'COPY':
        if os.path.isfile(cmd[1]) and os.path.isfile(cmd[2]):
            path = cmd[1] + ',' + cmd[2]
        else:
            out = False

    if out is False:
        return False, None, None
    return True, name, path

    # (6)


def handle_client_request(command, params):

    """
    Create the response to the client, given the command is legal and params are OK

    For example, return the list of filenames in a directory
    Note: in case of SEND_PHOTO, only the length of the file will be sent



    :param command: Command from the client
    :param params: Route to the content / command execution destination
    :return: response: the requested data
    """

    # (7)

    response = None

    if command == 'DIR':
        params = params + "\*.*"
        files_list = glob.glob(params)
        response = str(files_list)

    if command == 'DELETE':
        try:
            os.remove(params)
        except FileNotFoundError:
            return False
        else:
            response = 'OK'

    if command == 'COPY':
        my_file = params.split(',')
        try:
            shutil.copy(my_file[0], my_file[1])
        except FileNotFoundError:
            return False
        else:
            response = 'OK'

    if command == 'EXECUTE':
        try:
            subprocess.call(params)
        except FileNotFoundError:
            return False
        else:
            response = 'OK'

    if command == 'TAKE_SCREENSHOT':
        image = pyautogui.screenshot()
        image.save(PHOTO_PATH)
        response = 'OK'

    if command == 'SEND_PHOTO':
        try:
            my_photo = open(params, 'rb')
        except FileNotFoundError:
            return False
        else:
            my_file = my_photo.read()
            my_photo.close()
            response = my_file
    return response


def main():
    # open socket with client

    # (1)
    server_socket = socket.socket()
    server_socket.bind((IP, 8820))
    server_socket.listen()
    print("Server is up and running")

    (client_socket, client_address) = server_socket.accept()
    print("Client connected")
    # handle requests until user asks to exit
    while True:

        # Check if protocol is OK, e.g. length field OK
        valid_protocol, cmd = protocol.get_msg(client_socket)
        if valid_protocol:

            # Check if params are good, e.g. correct number of params, file name exists
            valid_cmd, command, params = check_client_request(cmd)
            if valid_cmd:
                # (6)

                if command != 'EXIT':
                    # prepare a response using "handle_client_request"
                    my_command_to_client = handle_client_request(command, params)
                    response = my_command_to_client

                    # add length field using "create_msg"
                    if command != 'SEND_PHOTO':
                        response_mag = protocol.create_msg(response)
                        # send to client
                        client_socket.send(response_mag.encode())

                    if command == 'SEND_PHOTO':
                        # Send the data itself to the client
                        # Message size
                        length = str(len(str(my_command_to_client)))

                        # Number of digits of message size
                        sie_of_length = str(len(length))

                        # Add '0' to a 4-digit sequence
                        zfill_length = sie_of_length.zfill(LENGTH_FIELD_SIZE)

                        # Send the number of digits of the message size
                        client_socket.send(zfill_length.encode())

                        # Send message size
                        client_socket.send(length.encode())

                        # Sending the message
                        client_socket.send(response)

                    # (9)
            else:
                # prepare proper error to client
                response = 'Bad command or parameters'
                response = protocol.create_msg(response)

                client_socket.send(response.encode())

            # send to client
            if cmd == 'EXIT':
                break
        else:
            # prepare proper error to client
            response = 'Packet not according to protocol'
            # send to client
            client_socket.send(response.encode())

            # Attempt to clean garbage from socket
            client_socket.recv(1024)
    # close sockets
    print("Closing connection")


if __name__ == '__main__':
    main()
