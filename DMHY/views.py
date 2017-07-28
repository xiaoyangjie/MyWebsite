# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from Function import DMHYFunction
# Create your views here.

api = DMHYFunction()

def DMHY(request):
    result = api.returnLatestContent()
    if not result :
        return render(request, 'DMHY/DMHYError.html')
    else:
        return render(request, 'DMHY/DMHY.html', {'content':result})

def DMHYTotal(request, pageNum):
    pageNum = int(pageNum)
    result = api.returnPageNumContent(pageNum)
    print result[1]
    if pageNum == 1:
        return render(request, 'DMHY/DMHYFirstPage.html' , {'content':result[0], 'pageNum':2, 'totalPage':result[1]})
    else:
        return render(request, 'DMHY/DMHYTotal.html' ,  {'content':result[0], 'pageNum':[pageNum + 1,pageNum,pageNum - 1], 'totalPage':result[1]})

def DMHYKeywords(request, pageNum):
    pageNum = int(pageNum)
    keyword = request.GET['keyword']
    result = api.findKeywords(pageNum, keyword)
    if pageNum == 1:
        return render(request, 'DMHY/DMHYKeywordsFirstPage.html' , {'content':result[0], 'pageNum':2 , 'keyword':keyword, 'totalPage':result[1]})
    else:
        return render(request, 'DMHY/DMHYKeywords.html' ,  {'content':result[0],'keyword':keyword,
                                                            'pageNum':[pageNum + 1,pageNum,pageNum - 1],'totalPage':result[1]})
