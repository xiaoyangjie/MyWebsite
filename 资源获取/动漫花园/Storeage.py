# coding=utf-8
import time
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import DuplicateKeyError, AutoReconnect, ServerSelectionTimeoutError
from Configure import MONGODB, EACHFINDNUMLIMIT


class Stroage(object):
    def __init__(self):
        self.dataStorage = {}
        self.__createUniqueIndex()
        for i in range(len(MONGODB)):
            self.dataStorage[MONGODB[i].get('name')] = MongoClient(MONGODB[i].get('host')).get_database(MONGODB[i].get('db'))\
                    .get_collection(MONGODB[i].get('col'))


    def __createUniqueIndex(self):
        for i in range(len(MONGODB)):
            if MONGODB[i].get('name') == 'DMHY':
                client = MongoClient(MONGODB[i].get('host'))
                if MONGODB[i].get('col') not in client[MONGODB[i].get('db')].collection_names():
                    ##############title建立唯一索引#############
                    client[MONGODB[i].get('db')][MONGODB[i].get('col')].create_index\
                    ([("title", ASCENDING)], name="title", unique=True)
                    ###############publishTime用于排序#############################
                    client[MONGODB[i].get('db')][MONGODB[i].get('col')].create_index \
                        ([("publishTime", DESCENDING)] , name="publishTime")

            ####################record不建索引##########################
            if MONGODB[i].get('name') == 'record':
                client = MongoClient(MONGODB[i].get('host'))
                if MONGODB[i].get('col') not in client[MONGODB[i].get('db')].collection_names():
                    content = {"lastestPublishTime" : int(time.time()),"captureWebsite" : "DMHY","pageNum" : 1,"isFinished" : False}
                    client[MONGODB[i].get('db')][MONGODB[i].get('col')].insert(content)

    def insert(self, name, insertContent):
        try:
            self.dataStorage.get(name).insert(insertContent)
        except DuplicateKeyError as DK:
            pass
        except AutoReconnect as AR:
            time.sleep(10 * 60)
            print AR.message

    def update(self, name, updateCondition=None ,updateContent=None):
        assert type(updateCondition) == dict
        assert type(updateContent) == dict
        try :
            self.dataStorage.get(name).update(updateCondition, {'$set':updateContent})
        except AutoReconnect as AR :
            time.sleep(10 * 60)
            print AR.message

    def findOne(self, name ,*args, **kwargs):
        print args
        flag = True
        result = False
        while flag:
            try:
                if len(args) == 1:
                    result = self.dataStorage.get(name).find_one(args[0])
                    flag = False
                elif len(args) == 2:
                    result = self.dataStorage.get(name).find_one(args[0], args[1])
                    flag = False
                else :
                    result = False
                    flag = False
            except AutoReconnect as AR :
                time.sleep(60 * 10)
                print AR.message
        return result

    def findMany(self, name ,*args, **kwargs):
        print args
        flag = True
        result = False
        while flag:
            try:
                if len(args) == 1:
                    result = self.dataStorage.get(name).find(args[0]).limit(EACHFINDNUMLIMIT)
                    flag = False
                elif len(args) == 2:
                    result = self.dataStorage.get(name).find(args[0], args[1]).limit(EACHFINDNUMLIMIT)
                    flag = False
                else:
                    result = False
                    flag = False
            except AutoReconnect as AR :
                time.sleep(60 * 10)
                print AR.message
        return result