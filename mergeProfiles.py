# merge name.p into profile.p
from RRRecorder import RenrenRecorder


storePath = 'D:/Projects/NetSci/U&I/data'
mergedRec = RenrenRecorder(path=storePath, writeBack=True)
profiles = mergedRec.getProfiles()

for rrID, name in mergedRec.getNames().items():
    if rrID in profiles:
        profiles[rrID]['名称'] = name
    else:
        profiles[rrID] = {'名称':name}

mergedRec.save()