import pickle


# relation.p里面是一个dictionary，key是renrenID，value是该renrenID的好友的renrenID集合（一个set）
# name.p里面也是一个dictionary，key是renrenID，value是对应显示的名字
class RenrenRecorder:
    def __init__(self, path, writeBack=False):
        self.load(path)
        self.writeBack = writeBack

    def __del__(self):
        if self.writeBack: self.save()

    def load(self, path):
        self.relationPath = path+'/relation.p'
        self.namePath = path+'/name.p'
        self.profilePath = path+'/profile.p'
        try:
            self.relation = pickle.load(open(self.relationPath, 'rb'))
        except FileNotFoundError:
            self.relation = {}
        try:
            self.name = pickle.load(open(self.namePath, 'rb'))
        except FileNotFoundError:
            self.name = {}
        try:
            self.profile = pickle.load(open(self.profilePath, 'rb'))
        except FileNotFoundError:
            self.profile = {}

    def save(self):
        pickle.dump(self.relation, open(self.relationPath, 'wb'))
        pickle.dump(self.name, open(self.namePath, 'wb'))
        pickle.dump(self.profile, open(self.profilePath, 'wb'))

    def addNames(self, nameList):
        self.name.update(nameList)

    def getNames(self):
        return self.name

    def addFriends(self, rrID, friendList):
        if rrID in self.relation:
            self.relation[rrID] = self.relation[rrID] | friendList
        else:
            self.relation[rrID] = friendList

    def getFriends(self, rrID):
        if rrID in self.relation:
            return self.relation[rrID]
        else:
            return {}

    def addRelations(self, relationList):
        for renrenId in relationList.keys():
            self.addFriends(renrenId, relationList[renrenId])

    def getRelations(self):
        return self.relation

    def setProfile(self, rrID, profile):
        self.profile[rrID] = profile
