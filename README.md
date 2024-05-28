# W-P-project
project that monitors and bans sites according to the users request. involves uses with databases, socket communication, registry handling

constants to change:
1. in the client_constants.py and server_constants.py make sure to change these constants:
   - BIG_SERVER_IP_CLIENT (to the ip of the computer that bigServer.py is running on)
   - html_file_path (to the correct path of the .html file on your computer)
   - bat_file_path (to the correct path of the .bat file on your computer)
2. in the .bat file:
   - make sure to change the contents of the .bat file to the path to where you keep the pServer.py file

how to run:
1. (ideally the server should be running at all times from a distant computer but if the server is down youll need to run the bigServer.py file)
2. run the GUI.py file on the computer you want the banning and monitoring to occur on, signup with a username and password and then go to settings > network & internet > use a proxy server > input the ip 127.0.0.1 and port 8888
3. from another computer run the GUI.py file and login with the information you previously chose, from there you can add / remove / view the list of banned sites
4. now when trying to enter a "banned site" from the computer you signed up on the site will be blocked and a custom html error page will open

behind the scenes (what the project actually does - heavily simplified):
1. starts running a main server (bigServer.py) to handle client requests and storing information in databases
2. after signing up saves information the registry to automatically sign in and run the code in case of computer restart
3. upon signup immediately starts running pServer.py file that runs a proxy server and acts as a man in the middle that has access to all requests out of the computer (for example the url of the reqeusted sites the computer wants to enter) - even has access to secure type (https) requests using the tunneling principle. if a banned site is detected in the url return an error code and custom html page
4. when logging in from a different computer you connect to the big server and can alter the banning information for the user you logged in as
