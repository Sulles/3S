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


class Message(object):
    def __init__(self, identifier, data, status=1):
        # assertion checks
        assert isinstance(identifier, str), "ERROR: 0010 - Identifier not type: string"
        assert isinstance(data, str), "ERROR: 0011 - Data not type: string"
        assert isinstance(status, int), "ERROR: 0012 - Status not type: int"

        self.__id = identifier
        self.__data = json.loads(data)
        self.__status = status

    # creates easily understandable string version of self
    def __str__(self):
        string = None
        try:
            string = str("Identifier...\n\t[" + self.__id + "]\nKeys...")
            for key in self.__data:
                string = string + str("\n\t{" + key + ":\t" + self.__data[key] + "}")
        except Exception as e:
            print("ERROR 0013 - Data not JSON compatible")
            raise
        finally:
            return string

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

    def update_status(self, new_status):
        assert isinstance(new_status, int), "ERROR: 0012 - Status not type: int"
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
