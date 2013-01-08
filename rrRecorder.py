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
        try:
            self.relation = pickle.load(open(self.relationPath, 'rb'))
        except FileNotFoundError:
            self.relation = {}
        try:
            self.name = pickle.load(open(self.namePath, 'rb'))
        except FileNotFoundError:
            self.name = {}
    
    def save(self):
        pickle.dump(self.relation, open(self.relationPath, 'wb'))
        pickle.dump(self.name, open(self.namePath, 'wb'))
    
    def getNames(self):
        return self.name
    
    def getRelationList(self):
        return self.relation
    
    def getFriends(self, renrenId):
        if renrenId in self.relation:
            return self.relation[renrenId]
        else:
            return {}
    
    def addRelation(self, renrenId, friendList):
        if renrenId in self.relation:
            self.relation[renrenId] = self.relation[renrenId] | friendList
        else:
            self.relation[renrenId] = friendList
    
    def mergeRelation(self, relationList):
        for renrenId in relationList.keys():
            self.addRelation(renrenId, relationList[renrenId])
    
    def addName(self, profileList):
        self.profile.update(profileList)