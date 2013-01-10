import os
from RRRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'
mergedRec = RenrenRecorder(path=storePath, writeBack=True)

#merge relationship network and names from different centers
for email in os.listdir(storePath):
    localRec = RenrenRecorder(storePath+'/'+email+'/renrenData')
    mergedRec.addRelations(localRec.getRelations())
    mergedRec.addNames(localRec.getNames())

#fix relationship network asymmetry due to that we grab pages at different times
relations = mergedRec.getRelations()
reverse = {}
for rrID1 in relations.keys():
    for rrID2 in relations[rrID1]:
        if rrID2 in reverse:
            reverse[rrID2] = reverse[rrID2] | {rrID1}
        else:
            reverse[rrID2] = {rrID1}
for rrID, friends in reverse.items():
    mergedRec.addFriends(rrID, friends)

mergedRec.save()
