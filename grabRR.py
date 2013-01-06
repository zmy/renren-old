#import time
from rrBrowser import RenrenBrowser
from rrParser import RenrenParser
#from rrDB import RenrenDb
from rrRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'
rrID = input("Your Renren ID (e.g.239486743): ")
rrUser = input("Your Renren Login Email: ")
rrPassword = input("Your Renren Password: ")

#db = RenrenDb()
browser = RenrenBrowser(user=rrUser, passwd=rrPassword, path=storePath)
browser.setLogLevel(40)
browser.login()
recorder = RenrenRecorder(path=browser.getPwdRoot(), writeBack=True)
parser = RenrenParser(browser, recorder)
#print(len(recorder.getFriends(rrID)))

#net1
browser.friendListPage(rrID)
parser.friends()
recorder.save()

#net2
#flist = db.getRenrenId(2, rrID)
myFriends = recorder.getFriends(rrID)
cnt = 0
for myFriend in myFriends:
    #loopStart=time.time()
    browser.friendListPage(myFriend)
    print("{}: {}'s friendship grabbed".format(cnt, myFriend))
    cnt = cnt+1
    #loopEnd=time.time()
    #if (loopEnd-loopStart<10):
    #    print('loop time={},parsering to kill time'.format(loopEnd-loopStart))
    #    parser.friends()
    #    kill=time.time()
    #    print('time cost ={}'.format(kill-loopEnd))
parser.friends()
