import os
from rrRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'
mergedRec = RenrenRecorder(path=storePath, writeBack=True)
for email in os.listdir(storePath):
    localRec = RenrenRecorder(storePath+'/'+email+'/renrenData')
    mergedRec.addRelations(localRec.getRelations())
    mergedRec.addNames(localRec.getNames())
mergedRec.save()
