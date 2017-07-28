# coding=utf-8


import time
from multiprocessing.dummy import Pool
from pymongo.errors import ServerSelectionTimeoutError
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains #引入ActionChains鼠标操作类
from selenium.webdriver.common.keys import Keys #引入keys类操作
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.common.by import By
import Parse
import Storeage
from Configure import PROXY

class DMHY(object):
    def __init__(self):
        self.__stroage = Storeage.Stroage()
        self.__chrome_options = webdriver.ChromeOptions()
        # self.__chrome_options.add_argument('--proxy-server=%s' % PROXY)
        self.__chrome_options.add_experimental_option("prefs", {'profile.default_content_setting_values.images': 2})
        self.__parse = Parse.Parse()


    def captureTotalOrUpdate(self, type='update'):
        self.__driver = webdriver.Chrome(chrome_options=self.__chrome_options)

        animationUrl = 'https://share.dmhy.org/topics/list/sort_id/2/page/'

        # keywordUrl = 'https://share.dmhy.org/topics/list?sort_id=2&keyword=air'

        isDriver = False
        flag = True
        DMHYRecord = self.__stroage.findOne('record',{'captureWebsite':'DMHY'})
        if type == 'update':
            pageNum = 1
        else :
            pageNum = DMHYRecord['pageNum']

        lastestPublishTime = 1
        isLastestTime = True   #用于找到最新发布时间

        while flag:
            ######################如果因为异常关闭浏览器，应该再次打开一个#########################
            if isDriver:
                self.__driver = webdriver.Chrome(chrome_options=self.__chrome_options)
                isDriver = False

            _animationUrl = animationUrl + str(pageNum)
            try :
                self.__driver.get(_animationUrl)
                WebDriverWait(self.__driver,timeout=30).until(EC.presence_of_element_located((By.CLASS_NAME,'header')))
                pageNum = pageNum + 1
                html = self.__driver.page_source
                contentList = self.__parse.DMHYAnimationHtmlParse(html)
                for content in contentList:
                    #######################################
                    if isLastestTime:
                        lastestPublishTime = content['publishTime']
                        isLastestTime = False
                    ##########################################
                    self.__stroage.insert('DMHY', content)
                    if content['publishTime'] < DMHYRecord['lastestPublishTime']:
                        # 用于判断是否更新完，这种可以防止如果更新过程中突然中断而采集不全的情况，牺牲了效率
                        self.__stroage.update('record', updateCondition={'captureWebsite': 'DMHY'},
                                              updateContent={'lastestPublishTime': lastestPublishTime})
                        flag = False
                        break

                ####################判断采集完成####################################
                if type != 'update':
                    text = self.__driver.find_element_by_css_selector('div.table.clear').find_element_by_css_selector(
                        'div.clear').find_element_by_css_selector('div').text
                    if text == u'沒有可顯示資源':
                        self.__stroage.update('record', updateCondition={'captureWebsite': 'DMHY'},
                                              updateContent={'isFinished': True})
                        break
                    self.__stroage.update('record', updateCondition={'captureWebsite': 'DMHY'},
                                          updateContent={'pageNum': pageNum})
            except NoSuchWindowException:
                isDriver = True
                continue
            except :
                isDriver = True
                try :
                    self.__driver.close()
                except WebDriverException:
                    pass
                time.sleep(30)
                continue

        self.__driver.close()
        print 'finish'

    def newlyCaptureTotal(self):
        pass

    #暂时弃用
    # def __animationCpature(self, animationUrl):
    #     isDriver = False
    #     isFinish = False
    #     while not isFinish:
    #         if isDriver:
    #             self.__driver = webdriver.Chrome(chrome_options=self.__chrome_options)
    #             isDriver = False
    #         try:
    #             self.__driver.get(animationUrl)
    #             WebDriverWait(self.__driver, timeout=30).until(
    #                 EC.presence_of_element_located((By.CLASS_NAME, 'header')))
    #             isFinish = True
    #         except:
    #             isDriver = True
    #             try:
    #                 self.__driver.close()
    #             except NoSuchWindowException:
    #                 pass
    #             except WebDriverException:
    #                 pass
    #             time.sleep(30)
    #             continue
    #     html = self.__driver.page_source
    #     content = {}
    #     try:
    #         content = self.__parse.DMHYEachAnimationParse(html)
    #     except:
    #         content['alive'] = False
    #     content['isRead'] = True
    #     self.__stroage.update('DMHY', updateCondition={'animationUrl': animationUrl['animationUrl']},
    #                           updateContent=content)
    def eachAnimationCapture(self):
        while True:
            try:
                if self._eachAnimationCapture():
                    break
                time.sleep(10 * 60)
            except:pass

    def _eachAnimationCapture(self):
        self.__driver = webdriver.Chrome(chrome_options=self.__chrome_options)
        animationUrls = []
        try:
            animationUrls = self.__stroage.findMany('DMHY',{'isRead':{'$exists':False}},{'_id':0,'animationUrl':1})
            if animationUrls.count() == 0:
                self.__driver.quit()
                return True
        except ServerSelectionTimeoutError as SSTE:
            print SSTE.message
            time.sleep(60 * 10)

        for animationUrl in animationUrls:
            print 'start capture :' + animationUrl['animationUrl']
            try:
                self.__driver.get(animationUrl['animationUrl'])
                WebDriverWait(self.__driver, timeout=30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'header')))
            except Exception:
                self.__driver.quit()
                return False

            html = self.__driver.page_source
            content = {}
            try:
                content = self.__parse.DMHYEachAnimationParse(html)
            except :
                content['alive'] = False
            content['isRead'] = True
            self.__stroage.update('DMHY',updateCondition={'animationUrl' : animationUrl['animationUrl']}, updateContent=content)

        self.__driver.quit()


if __name__ == '__main__' :
    dmhy = DMHY()
    while True:
        dmhy.captureTotalOrUpdate('update')
        dmhy.eachAnimationCapture()
        time.sleep(60 * 10)

    # dmhy.eachAnimationCapture()

