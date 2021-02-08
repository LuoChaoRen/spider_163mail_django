# ！/usr/bin/python3
# -*- coding: utf-8 -*-

import os,time
from urllib.request import urlopen
import requests,random
device_id = ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 32))
session = requests.session()
# "X-Forwarded-For":xfw,
def download_from_url(url, dst,cookie, sid, user_name,ua):
    # 获取文件长度
    try:
        file_size = int(urlopen(url).info().get('Content-Length', -1))
    except Exception as e:
        print(e)
        print("错误，访问url: %s 异常" % url)
        return False
    # 判断本地文件存在时
    if os.path.exists(dst):
        # 获取文件大小
        first_byte = os.path.getsize(dst)
    else:
        # 初始大小为0
        first_byte = 0

    # 判断大小一致，表示本地文件存在
    if first_byte >= file_size:
        print("文件已经存在,无需下载")
        return file_size

    header = {
        "Host": "mail.163.com",
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://mail.163.com/js6/main.jsp?sid="+sid+"&df=email163",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        'Cache-Control': 'no-cache'
    }
    # 访问url进行下载
    req = session.get(url,headers = header,stream=True,cookies=cookie)
    req.keep_alive = False
    if "温馨提醒：您今天的下载流量已超过当日最大限制，请明天再试!" in req.text:
        print("温馨提醒：您今天的下载流量已超过当日最大限制，请明天再试!")
        return False
    try:
        with(open(dst, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(e)
        return False

    # 下载完后发送一条请求
    dw_request_url = "https://countly.mail.163.com/stats/i?"
    dw_request_data = {
        "events": "[{'key':'read_attach_download_click','count':1,'segmentation':{'value':'1','sid':'"+sid+"'},'path_trace':[],'type':'click','module_name':'webmail_index_view','utm':{'utm_id':'','utm_source':'','utm_medium':'','utm_term':'','utm_content':'','utm_campaign':''},'domInfo':{'type':'click','x':0,'y':0,'width':1920,'height':562,'targetName':'','className':'','id':'','dataset':{}},'timestamp':"+str(int(round(time.time() * 1000)))+",'hour':11,'dow':2,'tz':480}]",
        "device_id": device_id,
        "version": "1.0",
        "common": "{'ua':'Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0','browser':'Firefox','browser_version':'70.0','os':'Linux','os_version':'x86_64','device':'desktop','resolution':'1920x1080','referrer':'https://mail.163.com/entry/cgi/ntesdoor?t="+str(int(round(time.time() * 1000)))+"','site_channel':'default','client':'pc','density':'@1x','locale':'zh-CN','manufacturer':'','domain':'mail.163.com','app_version':'6.0b2012241120','abtest_zone':'','abtest_version':'','carrier':'','app_channel':'','ip':'','lbs':'','network_type':'','uid':'"+user_name+"','dashi_uid':''}",
        "timestamp": str(int(round(time.time() * 1000))),
        "hour": "11", "dow": "2", "tz": "480"
    }
    dw_request_header = {
        "Host": "countly.mail.163.com",
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://mail.163.com",
        "Connection": "keep-alive",
        "Referer": "https://mail.163.com/js6/main.jsp?sid="+sid+"&df=email163",
        "TE": "Trailers"
    }
    rs = session.get(dw_request_url, params = dw_request_data,headers = dw_request_header,cookies=cookie)
    rs.keep_alive = False
    return True

if __name__ == '__main__':
    pass