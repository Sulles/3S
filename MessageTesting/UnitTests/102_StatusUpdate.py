"""
Created: March 30, 2019
Updated:

@author: Suleyman Barthe-Sukhera

This Unit Test will...
1. Verify that only the message status can be modified by:
    A. calling update_status
    B. attempting to
"""

import sys
sys.path.append("..")
from ..Message import Message
from time import time


msg_fields = {'id': 'return_data',
              'data_start': '{ "test": "hello world", '}

try:
    n = 10000
    print("(-) Creating " + str(n) + " test messages")
    messages = []
    for _ in range(n):
        messages.append(Message(msg_fields["id"],
                                str(msg_fields["data_start"]) + '"message_number": "' + str(_) + '" }'))
    print("(=) Created " + str(n) + " messages")

    start_time = time()
    for _ in messages:
        _.update_status(2)
    end_time = (time() - start_time) * 1000
    print("(A) Updated status for " + str(n) + " messages in " + str(end_time) +
          " ms -OR- " + str(int(end_time*10000/32)/100) + "% of the budget")

    try:
        # messages[0].__Message_id = 0
        messages[0].__Message_data = ""
    except ValueError:
        print("(B) Successfully failed to modify Message attribute")
    finally:
        # print("(B) Successfully failed to modify Message attribute")
        pass

except Exception as e:
    print("***** EXCEPTION RAISED: " + str(e))

finally:
    pass

