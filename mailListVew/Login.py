import requests
import time
import random
import json
import execjs
import re
import traceback
import os
class Login:
    def __init__(self,username,passwd,save_url):
        self.username = username+"@163.com"
        self.passwd = self.get_passwd(passwd)
        self.sid = ""
        self.save_url = save_url

    def get_passwd(self,p):
        js_url = os.path.dirname(os.path.dirname(__file__))+"/static/js/"
        f = open(js_url+ "get_pw.js", 'r', encoding='UTF-8')
        line = f.readline()
        jsstr = ''
        while line:
            jsstr = jsstr + line
            line = f.readline()
        ctx = execjs.compile(jsstr)
        pw = ctx.call('encrypt2',p)
        return pw

    def gettime(self):
        return str(round(time.time() * 1000))

    def get_radom(self,num):
        return ''.join(random.sample('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', num))

    def get_num_radom(self,num):
        return ''.join(random.sample('0123456789', num))

    def start_login(self):
        return self.request1()
        

    def request1(self):#get_l_s_mail163CvViHzl
        try:
            rtid = self.get_radom(32)
            utid = self.get_radom(32)
            times = self.gettime()
            MGID = self.gettime() +"."+self.get_num_radom(4)
            cookies = "utid=" + utid + ";"
            request_url = "https://dl.reg.163.com/dl/ini?pd=mail163&pkid=CvViHzl&pkht=mail.163.com&topURL=https://mail.163.com/&rtid=%s&nocache=%s"%(rtid,times)
            request_header = {
                "Host": "dl.reg.163.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Referer": "https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=%2F%2Fmimg.127.net%2Fp%2Ffreemail%2Findex%2Funified%2Fstatic%2F2020%2F%2Fcss%2F&cf=urs.163.4944934a.css&MGID=" + MGID + "&wdaId=&pkid=CvViHzl&product=mail163",
                "Cookie": cookies,
            }
            sessions1 = requests.session()
            sessions1.keep_alive = False
            response = sessions1.get(url=request_url,headers = request_header)
            cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
            for key in cookies_dict:
                cookies = cookies + key+"="+ cookies_dict[key]+ ";"
            sessions1.close()
            return self.request2(cookies,rtid)
        except:
            traceback.print_exc()
            return 0

    def request2(self,cookies,rtid):
        try:
            MGID = self.gettime() + "." + self.get_num_radom(4)
            request_url = "https://dl.reg.163.com/dl/gt?un={0}&pkid=CvViHzl&pd=mail163&channel=0&topURL=https%3A%2F%2Fmail.163.com%2F&rtid={1}&nocache={2}".format(self.username,rtid,self.gettime())
            request_header = {
                "Host": "dl.reg.163.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Referer": "https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=%2F%2Fmimg.127.net%2Fp%2Ffreemail%2Findex%2Funified%2Fstatic%2F2020%2F%2Fcss%2F&cf=urs.163.4944934a.css&MGID="+MGID+"&wdaId=&pkid=CvViHzl&product=mail163",
                "Cookie": cookies,
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
            sessions2 = requests.session()
            sessions2.keep_alive = False
            response = sessions2.get(url=request_url,headers = request_header)
            sessions2.close()
            tk_dict = json.loads(response.text)
            if tk_dict["ret"] == "201":
                return self.request3(tk_dict["tk"],rtid,cookies)
            else:
                print(tk_dict)
                return 0
        except:
            traceback.print_exc()
            return 0

    def request3(self,tk,rtid,cookies):
        # cookies = cookies+"JSESSIONID-WYTXZDL=7Emj1byhaX5lIWnyahTHzLt5eILv%2Fqm%2BLyZ%2BHBuFnjdYjZrs%2Blum0eh07uk9u1HTzzB2Ea7A%2Bpk4PvS3msLFTXHx7S7z26nqqfKdxwdifn0vjpHVZUR0DqiWfW33xR7pTpjM%5CcBSGtfzslVkMufySmHhq6vOD4NObo7nUIXwHFT2yB%2Bj%3A"+self.gettime()+";"
        try:
            MGID = self.gettime() + "." + self.get_num_radom(3)
            request_url = "https://dl.reg.163.com/dl/l"
            request_header = {
                "Host": "dl.reg.163.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json",
                "Origin": "https://dl.reg.163.com",
                "Connection": "keep-alive",
                "Referer": "https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=%2F%2Fmimg.127.net%2Fp%2Ffreemail%2Findex%2Funified%2Fstatic%2F2020%2F%2Fcss%2F&cf=urs.163.4944934a.css&MGID="+MGID+"&wdaId=&pkid=CvViHzl&product=mail163",
                "Cookie": cookies,
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            }
            request_data = {
                "un":self.username,
                "pw":self.passwd,
                "pd":"mail163",
                "l":0,
                "d":10,
                "t":int(self.gettime()),
                "pkid":"CvViHzl",
                "domains":"",
                "tk":tk,
                "pwdKeyUp":1,
                "channel":0,
                "topURL":"https://mail.163.com/",
                "rtid":rtid
            }
            request_data  = json.dumps(request_data,separators=(',', ':'))
            sessions3 = requests.session()
            sessions3.keep_alive = False
            sessions3.cookies.clear()
            response = sessions3.post(url=request_url,data=request_data, headers=request_header)
            cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
            cookies += "starttime=;"
            for key in cookies_dict:
                cookies = cookies + key+"="+ cookies_dict[key]+ ";"
            sessions3.close()
            return self.request4(cookies)
        except:
            traceback.print_exc()
            return 0

    def request4(self,cookies):
        try:
            request_url = "https://mail.163.com/entry/cgi/ntesdoor?"
            request_header = {
                "Host": "mail.163.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://mail.163.com",
                "Connection": "keep-alive",
                "Referer": "https://mail.163.com/",
                "Cookie": cookies,
                "Upgrade-Insecure-Requests": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "Trailers",
            }
            request_data = {
                "style": "-1",
                "df": "mail163_letter",
                "allssl": "true",
                "net": "",
                "language": "-1",
                "from": "web",
                "race": "",
                "iframe": "1",
                "url2": "https://mail.163.com/errorpage/error163.htm",
                "product": "mail163"
            }
            session4 = requests.session()
            session4.keep_alive = False
            session4.cookies.clear()
            response = session4.post(url=request_url,data=request_data,headers = request_header)
            session4.close()
            cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
            cookies_data = {}
            if "sid" in response.text:
                print("登录成功")
                rex = re.compile('sid=(.*?)&', re.S)
                self.sid = re.search(rex, response.text).group(1)
                cookies_data["Coremail.sid"] = self.sid
                for item in cookies_dict:
                    cookies_data[item] = cookies_dict[item]
                COOKIE  = json.dumps(cookies_data)
                with open(self.save_url+"cookies.json","w") as ck_f:
                    ck_f.write(COOKIE)
                ck_f.close()
                return 1
            else:
                return 0
        except:
            traceback.print_exc()
            return 0

if __name__ == '__main__':
    username = "luotao202012"
    passwd = "luotao2020123"
    login = Login(username,passwd,"")
    result = login.start_login()
    print(result)
