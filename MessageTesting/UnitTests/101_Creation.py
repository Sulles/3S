"""
Created: March 30, 2019
Updated:

@author: Suleyman Barthe-Sukhera

This Unit Test will...
1. Determine how long it takes to instantiate n messages
2. Ensure each message created is unique (should not be a problem, but best to be sure)
"""

import sys
sys.path.append("..")
from Message import Message
from time import time

msg_fields = {'id': 'return_data',
              'data_start': '{ "test": "hello world", '}

try:
    n = 1000
    print("(1) Creating " + str(n) + " messages took...")
    start_time = time()
    messages = []
    for _ in range(n):
        messages.append(Message(msg_fields["id"],
                                str(msg_fields["data_start"]) + '"message_number": "' + str(_) + '" }'))
    end_time = (time()-start_time)*1000
    print(str(end_time) + " ms -OR- " + str(int(end_time*10000/32)/100) + "% of the budget")

    # doing string compare to ensure uniqueness, so need to get string version of each message first
    message_strings = []
    for m in messages:
        message_strings.append(m.__str__())
    for x in range(1,len(messages)):
        if message_strings[x-1] in message_strings[x:]:
            print("ERROR 101: message " + str(x) + " not unique!")
    print("(2) Uniqueness verified")

    print("UNIT TEST 101 SUCCESSFUL")

except Exception as e:
    print("***** EXCEPTION RAISED: " + str(e))

finally:
    pass

