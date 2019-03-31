"""
Created: March 30, 2019
Updated:

@author: Suleyman Barthe-Sukhera

This Unit Test is meant to create multiple messages and ensure no data overlaps occur

TODO: Look into NUMPY array allocation with objects in array
"""

import sys
sys.path.append("..")
from Message import Message
from time import time

msg_fields = {'id': 'return_data',
              'data_start': '{ "test": "hello world", '}

try:
    n = 1000
    print("(*) Creating " + str(n) + " messages took...")
    start_time = time()
    messages = []
    for _ in range(n):
        messages.append(Message(msg_fields["id"],
                                str(msg_fields["data_start"]) + '"message_number": "' + str(_) + '" }'))
    end_time = (time()-start_time)*1000
    print(str(end_time) + " ms -OR- " + str(int(end_time*10000/32)/100) + "% of the budget")

    # TODO: Go through all messages and ensure they are all unique

    print("UNIT TEST 001 SUCCESSFUL")

except Exception as e:
    print("***** EXCEPTION RAISED: " + str(e))

finally:
    pass

