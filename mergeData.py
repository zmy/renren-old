import os
from rrRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'
mergedRec = RenrenRecorder(path=storePath, writeBack=True)
for email in os.listdir(storePath):
    localRec = RenrenRecorder(storePath+'/'+email+'/renrenData')
    mergedRec.mergeRelation(localRec.getRelationList())
    mergedRec.addProfile(localRec.getProfileList())
mergedRec.save()