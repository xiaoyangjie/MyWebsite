# coding=utf-8
"""
author = YJ

create time = 2017/4/6

history :

"""
import time

import Storeage
from lxml import etree


class Parse(object):
    def __init__(self):
        pass

    #################可以分离，但是现在还没有###########################
    def DMHYAnimationHtmlParse(self, html=''):
        htmlPage = etree.HTML(html)
        result = []
        DMHYUrl = 'https://share.dmhy.org'
        for i in htmlPage.xpath('//div[@class="table clear"]//div[@class="clear"]//tbody/tr'):
            r = {}
            try:
                r['publishTimeStr'] = i.xpath('.//td//span')[0].text
                # print r['publishTimeStr']
                r['publishTime'] = int(time.mktime(time.strptime(r['publishTimeStr'], "%Y/%m/%d %H:%M")))
                # print r['publishTime']
                r['classification'] = i.xpath('.//td//a//font')[0].text
                r['title'] = i.xpath('.//td[@class="title"]//a[@target="_blank"]')[0].text
                r['animationUrl'] = DMHYUrl + i.xpath('.//td[@class="title"]//a[@target="_blank"]')[0].attrib['href']
                r['contentSize'] = i.xpath('.//td[@nowrap="nowrap"]')[1].text
                r['publisher'] = i.xpath('.//td[@align="center"]//a')[-1].text

                print r
                # dataStorage.insert(name, r)
                result.append(r)
            except Exception:
                print Exception.message

        # print result
        return result


    ###############通过url去更新数据库，主要这样可以做到采集与解析与储存分离###################
    def DMHYEachAnimationParse(self, html=''):
        htmlPage = etree.HTML(html)
        r = {}
        r['image'] = ''
        try:
            r['image'] = htmlPage.xpath('//div[@class="topic-nfo box ui-corner-all"]//p//img')[0].attrib['src']
        except:
            pass
        r['torrent'] = 'http:' + htmlPage.xpath('//div[@id="tabs-1"]//p//a')[0].attrib['href']
        r['manget'] = htmlPage.xpath('//div[@id="tabs-1"]//p//a[@class="magnet"]')[0].attrib['href']

        return r

