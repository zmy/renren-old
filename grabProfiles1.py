# This script grabs profiles of the direct friends of the input user
# You should only run this script after successfully running mergeRelations.py
import time
from RRBrowser import RenrenBrowser
from RRParser import RenrenParser
from RRRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'

rrID = input("Your Renren ID (e.g.239486743): ")
rrUser = input("Your Renren Login Email: ")
rrPassword = input("Your Renren Password: ")

browser = RenrenBrowser(user=rrUser, passwd=rrPassword, path=storePath)
browser.setLogLevel(40)
browser.login()
mergedRec = RenrenRecorder(path=storePath, writeBack=True)
parser = RenrenParser(browser, mergedRec)

cnt = 0
friends = mergedRec.getFriends(rrID)
for rrID in friends:
    cnt += 1
    result = browser.grabProfilePage(rrID)
    print('√ {}: {}/{} {}'.format(rrID, cnt, len(friends), result))
    if result!='skipped':
        time.sleep(10)

parser.profiles()
mergedRec.save()
