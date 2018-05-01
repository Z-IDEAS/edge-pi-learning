# coding=utf-8
import socket  
import threading  
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--ip", required=True,
    help="ip of server")
args = vars(ap.parse_args())


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
  
sock.bind((args['ip'], 12345))  
  
sock.listen(5)  
print('Server '+socket.gethostbyname(args['ip'])+' is listening...')  

mydict = dict()  
mylist = list()  
  
def tellOthers(exceptNum, whatToSay):  
    c = [connection for connection, name in mylist if name == exceptNum][0]
    try:  
        c.send(whatToSay.encode())
    except:  
        pass  
  
def subThreadIn(myconnection, connNumber):  
    nickname = myconnection.recv(1024).decode()  
    mydict[myconnection.fileno()] = nickname  
    mylist.append((myconnection,nickname))
    print 'connection {} has nickname: {}'.format(connNumber, nickname)
    while True:  
        try:  
            recvedMsg = myconnection.recv(1024).decode()  
            if recvedMsg:
                recvedSplit = recvedMsg.split(';')
                for s in recvedSplit:
                    if s != '':
                        recvData = s.split(':')
                        print '{}->{}\n'.format(mydict[connNumber],recvedMsg)
                        tellOthers(recvData[0], '{};'.format(recvData[1]))
  
        except:
            return  
  
while True:  
    connection, addr = sock.accept()  
    print 'Accept a new connection {} {}'.format(connection.fileno(), connection.getsockname())
    try:  
        #connection.settimeout(5)  
        buf = connection.recv(1024).decode()  
        if buf == '1':  
            mythread = threading.Thread(target=subThreadIn, args=(connection, connection.fileno()))  
            mythread.setDaemon(True)  
            mythread.start()  
              
        else:  
            connection.close()  
    except : 
        pass 