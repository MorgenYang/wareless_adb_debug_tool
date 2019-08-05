import subprocess
import os
import commands
import re

PRE_CMD = 'adb shell "%s"'
KEYEVENT_CMD = 'adb shell input keyevent "%s"'          #event
KEYSWIPE_CMD = 'adb shell input swipe %s %s %s %s'      #x1, y1 ,x2 ,y2
KEYTAP_CMD = 'adb shell input tap %s %s'                #x1, y1

'''=======================================================
    Using subprocess as the thread to implement
    -subprocess.PIPE means output type as file
    -shell = True, means the cmd type could be sequence
    it should consider the space & metacharacters
    <This method would read until the msg done>
======================================================='''

def shell(cmd = None, shell_cmd = None, para = None):

    command = cmd
    if shell_cmd == "SHELL":
        command = PRE_CMD % (cmd)
    elif shell_cmd == "KEYEVENT":
        command = KEYEVENT_CMD % (str(para))
    elif shell_cmd == "SWIPE":
        command = KEYSWIPE_CMD % (str(para[0]), str(para[1]), str(para[2]), str(para[3]))
    elif shell_cmd == "TAP":
        command = KEYTAP_CMD % (str(para[0]), str(para[1]))
        
    #print (command)
    
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    
    return p.stdout.read()

'''=======================================================
    During the process get the process msg
    -It should set to the thread queue
    -Set the callback function to implement other function
======================================================='''
def keep_listen_shell(cmd, callback = None):
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    while True:
        l = p.stdout.readline()
        if not l:
            break
        print (l)
'''
try:
    keep_listen_shell("adb shell getevent -r")
    #keep_listen_shell("adb devices")
except:
    pass
'''
