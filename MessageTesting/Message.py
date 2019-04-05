"""
Created: March 30, 2019
Updated:

@author: Suleyman Barthe-Sukhera

Message object function: Contain 'MessageTypeIdentifier' and 'Data' attributes to facilitate message
    sending, receiving, and handling between server and clients

    - identifier = string
    - data = json structure
    - status:
        IN_TRANSIT = 1
        DELETE = 0
"""

import json
from copy import deepcopy


class Message(object):
    def __init__(self, identifier, data, status=1, spawn_point=[0, 0]):
        # assertion checks
        assert isinstance(identifier, str), "ERROR: M001 - Identifier not type: string"
        assert isinstance(data, str), "ERROR: M002 - Data not type: string"
        assert isinstance(status, int), "ERROR: M003 - Status not type: int"
        assert isinstance(spawn_point, list), "ERROR: M004 - Spawn point not type: list"
        assert len(spawn_point) == 2, "ERROR: M004.1 - Spawn point not of length 2"

        self.__id = identifier
        self.__data = json.loads(data)
        self.__status = status
        self.__spawn_point = spawn_point
        self.__radius = 0

    # creates easily understandable string version of self
    def __str__(self):
        string = None
        try:
            string = str("Identifier...\n\t[" + self.__id + "]\nKeys...")
            for key in self.__data:
                string = string + str("\n\t{" + key + ":\t" + self.__data[key] + "}")
        except Exception as e:
            raise ValueError("ERROR: M004 - Data not JSON compatible")
        finally:
            return string

    # def __setattr__(self, key, value):
    #     if value is None:
    #         pass
    #     elif key != "__Message_status":
    #         raise ValueError("ERROR: M005 - Message attribute '" + str(key) + "' attempted to be modified!")
    #     else:
    #         pass


    def display(self):
        print(self.__str__())

    def get_id(self):
        return str(self.__id)

    def get_data(self):
        return str(self.__data)

    def get_status(self):
        return self.__status

    def get_data_param(self, param):
        return self.__data[param]

    def get_spawn_point(self):
        return deepcopy(self.__spawn_point)

    def update_status(self, new_status):
        assert isinstance(new_status, int), "ERROR: M003 - Status not type: int"
        self.__status = new_status


def return_data(something):
    test = json.loads(something)
    return test['test']


if __name__ == '__main__':
    data = '{ "test": "hello world" }'
    my_message = Message('testMsg', data)

    message_handler_dict = {}
    message_handler_dict['testMsg'] = return_data

    print("Message Identifier:\t" + str(my_message.get_id()))
    print("Message Data:\t\t" + str(my_message.get_data()))
    print("Message Object printer...")
    my_message.display()
    print("Message Handler: " + message_handler_dict[my_message.get_id()](my_message.get_data()))
