# 3S
Solar System Simulator (3S)
# Authors
Soren Rademacher, Suleyman Barthe-Sukhera
# Original Concept by
Soren Rademacher
# UI, Design, and Programming by
Suleyman Barthe-Sukhera, Soren Rademacher
# Font by
Jyrki Ihalainen (yardan74@gmail.com)

# INSTRUCTIONS
To run 3S, either download 3S.exe in the master branch, or go to the Distribution branch and choose which version of 3S you wish to use

# SERVER INSTRUCTIONS
On Windows, cmd> netstat -a to determine what your LAN ip address is (i.e. 192.168.8.101)

In "server.py" change the second to last line so it looks like...

  websockets.serve(main, host='YOUR:IP:ADDRESS:HERE', port=6789))
  
Similarly, change line 5 on final.js so it looks like...

  var Connection = new WebSocket('ws://YOUR:IP:ADDRESS:HERE:6789/');
  
To run the server, simply cmd> python server.py


# CLIENT INSTRUCTIONS
Create any folder (Folder_A) and save the index.html file there

Within that folder (Folder_A), create a new folder titled "js"

Save the final.js doc (found within /js) to your "js" folder

>"Folder_A"

->index.html

>Folder "js"

-->final.js

