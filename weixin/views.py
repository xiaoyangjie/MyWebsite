# coding=utf-8
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic.base import View
import hashlib
import json
from lxml import etree
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage
from DMHY.Function import DMHYFunction
# Create your views here.

WEIXIN_TOKEN = 'xiaoyangjie'
AppID = 'wxd9f3de4d0ab3b45e'
AppSecret = 'f58092f44bb15b0996ddca664f4c5bc2'

# 实例化 WechatBasic
wechat_instance = WechatBasic(
    token=WEIXIN_TOKEN,
    appid=AppID,
    appsecret=AppSecret
)


@csrf_exempt
def test1(request):
    if request.method == 'GET':
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        if not wechat_instance.check_signature(
                signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')

        return HttpResponse(
            request.GET.get('echostr', ''), content_type="text/plain")

    # 解析本次请求的 XML 数据
    try:
        wechat_instance.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest('Invalid XML Data')

    # 获取解析好的微信请求信息
    message = wechat_instance.get_message()

    # 关注事件以及不匹配时的默认回复
    response = wechat_instance.response_text(
        content=(
            '感谢您的关注！\n回复【功能】两个字查看支持的功能，还可以回复任意内容开始聊天'
            '\n【<a href="http://www.ziqiangxuetang.com">自强学堂手机版</a>】'
        ))
    return HttpResponse(response, content_type="application/xml")

class WeixinInterface(View):
    def __init__(self):
        View.__init__(self)
        self.DMHYFunction = DMHYFunction()

    def get(self, request):
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = WEIXIN_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin  index")
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        # signature = request.GET.get('signature')
        # timestamp = request.GET.get('timestamp')
        # nonce = request.GET.get('nonce')
        #
        # if not wechat_instance.check_signature(
        #         signature=signature, timestamp=timestamp, nonce=nonce):
        #     return HttpResponseBadRequest('Verify Failed')
        #
        # return HttpResponse(
        #     request.GET.get('echostr', ''), content_type="text/plain")

    def post(self, request):
        # 解析本次请求的 XML 数据
        try:
            wechat_instance.parse_data(data=request.body)
        except ParseError:
            return HttpResponseBadRequest('Invalid XML Data')

            # 获取解析好的微信请求信息
        message = wechat_instance.get_message()

        # 关注事件以及不匹配时的默认回复
        response = wechat_instance.response_text(
            content=(
                '感谢您的关注！\n回复【功能】两个字查看支持的功能。'
                '\n【<a href="http://121.49.99.14/home">杨杰资源</a>】'
            ))
        if isinstance(message, TextMessage):
            # 当前会话内容
            content = message.content.strip()
            reply_text = '感谢您的关注！\n回复【功能】两个字查看支持的功能。\n【<a href="http://121.49.99.14/home">杨杰资源</a>】'
            if content == u'功能':
                reply_text = (
                    '目前支持的功能：\n1. 关键词后面加上【搜索】两个字可以根据关键词搜索动画，得到最新的最多10条信息'
                    '比如回复 "clannad搜索"\n'
                    '2. 回复"最新动画"将有最新的10条动画资源\n'
                    '还有更多功能正在开发中哦 ^_^\n'
                    '【<a href="http://121.49.99.14/home">杨杰资源</a>】'
                )
            elif content == u'最新动画':
                reply_text = ''
                result = self.DMHYFunction.returnLatestContent()
                for i in result:
                    reply_text = reply_text + '发布时间：' + (i['publishTimeStr'].encode('utf-8')) + '\n' + '发布主题：' + (i['title'].encode('utf-8')) + '\n\n'

            elif content.endswith(u'搜索'):
                reply_text = ''
                keywords = content.split(u'搜索')[0]
                result = self.DMHYFunction.findKeywords(1 , keywords)
                if result == []:
                    reply_text = '没有相关内容'
                else:
                    for i in result:
                        try:
                            reply_text = reply_text + '发布时间：' + (i['publishTimeStr'].encode('utf-8')) + '\n' + '发布主题：' + (
                            i['title'].encode('utf-8')) + '\n\n'
                        except:pass

            elif content.endswith(u'教程'):
                reply_text = '您要找的教程如下：'

            response = wechat_instance.response_text(content=reply_text)

        return HttpResponse(response, content_type="application/xml")

    @csrf_exempt  # override
    def dispatch(self, *args, **kwargs):
        return super(WeixinInterface, self).dispatch(*args, **kwargs)

