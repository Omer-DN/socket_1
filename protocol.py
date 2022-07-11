#   Author: Omer Dayan - 312409386
#   11/11/2021

LENGTH_FIELD_SIZE = 4
PORT = 8820


def check_cmd(data):
    """
    Check if the command is defined in the protocol, including all parameters
    For example, DELETE c:\work\file.txt is good, but DELETE alone is not
    """
    list_valid = ['TAKE_SCREENSHOT', 'SEND_PHOTO', 'DIR', 'DELETE', 'COPY', 'EXECUTE', 'EXIT']
    if data == 'EXIT' or data == 'SEND_PHOTO':
        return True

    else:
        index = data.find(' ')
        cmd = data[:index]
        params = data[index:]
        return cmd in list_valid and params is not None

    # (3)


def create_msg(data):
    """
    Create a valid protocol message, with length field
    """

    # (4)
    if type(data) == list:
        data = ''.join(data)
    length = str(len(data))
    zfill_length = length.zfill(LENGTH_FIELD_SIZE)
    data = zfill_length + data

    return data


def get_msg(my_socket):
    """
    Extract message from protocol, without the length field
    If length field does not include a number, returns False, "Error"
    """

    # (5)
    length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
    if length.isdigit() is False:
        return False, None

    message = my_socket.recv(int(length)).decode()
    return True, message
