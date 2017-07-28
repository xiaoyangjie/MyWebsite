
MONGOHOST = 'mongodb://mongo:123456@222.197.180.150'
from pymongo import MongoClient
from time import *

class DMHYFunction(object):
    def __init__(self):
        self.cli = MongoClient(MONGOHOST)['test']['DMHY']
        self.totalPage = 0
        self.totalContent = {}
        self.returnContent = {}
        self.latestContent = {}
        self.forwordTime = 0
        self.backTime = int(time())

    def updateTotalContent(self, skipNum):
        self.backTime = int(time())
        self.totalPage = (self.cli.find().count() - 1) / 10 + 1
        if skipNum > 100:
            self.totalContent = [i for i in self.cli.find({}).sort('publishTime', -1).skip(skipNum * 10).limit(10)]
        elif self.backTime > (self.forwordTime + 60 * 10):
            self.totalContent = [i for i in self.cli.find({}).sort('publishTime',-1).limit(1000)]
            self.forwordTime = self.backTime

    def returnLatestContent(self):
        self.updateTotalContent(0)
        if len(self.totalContent) == 0:
            return False
        elif len(self.totalContent) < 10:
            self.latestContent = self.totalContent[0:len(self.totalContent)]
        else:
            self.latestContent = self.totalContent[0:10]
        return self.latestContent

    def returnPageNumContent(self, pageNum):
        self.updateTotalContent(pageNum - 1)
        self.returnContent = []
        if pageNum > 100 :
            if len(self.totalContent) != 0:
                self.returnContent = self.totalContent
        elif len(self.totalContent) < pageNum * 10 and len(self.totalContent) > (pageNum - 1) * 10:
            self.returnContent = self.totalContent[(pageNum - 1) * 10:len(self.totalContent)]
        else:
            self.returnContent = self.totalContent[(pageNum - 1) * 10:pageNum * 10]
        return (self.returnContent,self.totalPage)

    def findKeywords(self, pageNum, keyword):
        pageNum = pageNum - 1
        total = (self.cli.find({'title':{'$regex':keyword}}).count() - 1)/ 10 + 1
        r = [i for i in self.cli.find({'title':{'$regex':keyword}}).sort('publishTime', -1).skip(pageNum * 10).limit(10)]
        return (r,total)
