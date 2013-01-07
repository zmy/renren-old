from rrBrowser import RenrenBrowser
from rrRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'
mergedRec = RenrenRecorder(path=storePath)
print(len(mergedRec.getProfileList()))

rrID = input("Your Renren ID (e.g.239486743): ")
rrUser = input("Your Renren Login Email: ")
rrPassword = input("Your Renren Password: ")

