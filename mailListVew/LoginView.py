import traceback
import time
import re,json
import requests
import os
import random
import mailListVew.download as download
import pdfplumber
import subprocess,docx,pptx
from xlrd import open_workbook # xlrd用于读取xld
from fake_useragent import UserAgent
from mailListVew.es_models import Mail
from mailListVew.xzip import un_zip,un_7z,un_gz,un_rar,un_tar,b_7z,b_7z_dir,rm_file_or_dir
from mailListVew.Login import Login
from w3lib.html import remove_tags
from time import sleep
from mailListVew.tasks import async_call
import logging
logger = logging.getLogger('spider')
cookies_flg = 0
#获取ip
# get_ip = GetIP()
class LoginView():
    def __init__(self,name,passwd,get_id,add_flg):
        ua = UserAgent()
        self.USER_AG = ua.random
        self.SID = ""
        self.COOKIE = dict()
        self.login_num = 0
        self.email_name = name
        self.pwd = passwd
        self.save_url = os.path.dirname(os.path.dirname(__file__))+"/static/email_data/"#+数据文件
        if not os.path.exists(self.save_url):
            os.makedirs(self.save_url)
        self.eml_data = {}
        self.get_id_list = get_id #爬取过的id
        self.add_flg = add_flg  #重新爬or增量爬
        LOG_PATH = os.path.dirname(os.path.dirname(__file__))+"/static/log"
        rm_file_or_dir(LOG_PATH)
        if not os.path.isdir(LOG_PATH):
            os.mkdir(LOG_PATH)
            f = open(LOG_PATH+"/log.txt","w")
            f.close()
        self.save_flg = 1

    def dologin(self):
        logger.info('获取进度:%s' % "开始登录邮箱")
        print("开始登录邮箱")
        global cookies_flg
        try:
            login = Login(self.email_name,self.pwd,self.save_url)
            result = login.start_login()
            #登录成功
            if result == 1:
                with open(self.save_url+"/cookies.json", "r") as ck_f:
                    COOKIE = ck_f.read()
                self.COOKIE = json.loads(COOKIE)
                self.SID = self.COOKIE["Coremail.sid"]
                cookies_flg = 1
                return 1
            else:
                if self.login_num < 2:#重试
                    self.login_num += 1
                    time.sleep(3)
                    #重新登陆
                    self.dologin()
                else:
                    return 0
        except:
            traceback.print_exc()
    #定时反馈cookie防止过期
    def request_send(self):
        pass
    #通过非selenium方法getemail

    @async_call
    def start_spider(self):
        self.get_email_list()

    def get_email_list(self):
        # SID = self.SID
        global cookies_flg
        if self.SID:
            print("get_cookie_SID ok")
            logger.info("get_cookie_SID ok")
            try:
                time.sleep(3)
                #随机数
                random3_str = ''.join(str(i) for i in random.sample(range(0, 9), 3))
                random5_str = ''.join(str(i) for i in random.sample(range(0, 9), 5))
                # requests.adapters.DEFAULT_RETRIES = 5
                s = requests.session()
                s.keep_alive = False
                request_url = "https://mail.163.com/js6/s?sid="+self.SID+"&func=mbox:listMessages&Js6PromoteScriptLoadTime=1775&welcome_yx_red=1&mbox_folder_enter=1&stay_module=welcome,"+str(int(round(time.time() * 1000))-int(random3_str))+","+str(int(round(time.time() * 1000)))+","+random5_str
                rs = requests.post(request_url,cookies=self.COOKIE)
                if rs.status_code == 200:
                    if rs.url != request_url:
                        print("request error:url=",rs.url)
                        logger.info("request error:url=",rs.url)
                        return 0
                    with open(self.save_url+"/eml_list.xml",'w') as wt_ls_f:
                        wt_ls_f.write(rs.text)
                    wt_ls_f.close()
                else:
                    print(str(rs.status_code)+":\n"+rs.text)
                    logger.info(str(rs.status_code)+":\n"+rs.text)
                    with open(self.save_url+"/cookies.json","w") as delcookie_f:
                        delcookie_f.truncate()
                    delcookie_f.close()
                    if self.dologin() == 1:
                        self.get_email_list()
                    else:
                        print("dologin error")
                        logger.info("dologin error")
                        return "dologin error"
                return self.get_email_info()
            except Exception as e:
                print("get_email_list ERROR",e)
                logger.info("get_email_list ERROR",e)
                return 0

        else:
            print("no sid get_cookie_SID start")
            logger.info("no sid get_cookie_SID start")
            if os.path.exists(self.save_url+"/cookies.json") and os.path.getsize(self.save_url+"/cookies.json") > 0:
                cookies_flg = 1
            if cookies_flg:
                with open(self.save_url+"/cookies.json", "r") as cookie_f:
                    cookies = cookie_f.read()
                self.COOKIE = json.loads(cookies)
                self.SID = self.COOKIE["Coremail.sid"]
                cookie_f.close()
                if self.COOKIE["MAIL_MISC"] != self.email_name:
                    rm_file_or_dir(self.save_url+"/cookies.json")
                    if self.dologin() == 1:
                        self.get_email_list()
                    else:
                        print("新用户登录失败")
                        return 0
                else:
                    self.get_email_list()
            else:
                print("没有cookie")
                logger.info("没有cookie")
                if self.dologin()==1:
                    self.get_email_list()
                else:
                    return "no cookie error"
        # print("getover")
    def get_email_info(self):
        print("开始提取邮件信息")
        logger.info("开始提取邮件信息")
        try:
            with open(self.save_url+"/eml_list.xml","r") as emllist_f:
                ff = emllist_f.read()
                var_name_id = re.findall('.*<string name="id">(.*?)</string>.*', ff)
                for item in var_name_id:
                    re_id = item.replace(":", '').replace("+", '').replace("-", '')
                    #判断是增量爬取还是覆盖爬取
                    #增量爬取
                    if self.add_flg:
                        #判断item的id是否之前请求过
                        if re_id not in self.get_id_list:
                            self.get_info(item,re_id,1)
                        else:
                            pass
                        # 覆盖爬取
                    else:
                        self.get_info(item, re_id,0)
                emllist_f.close()
            return 1
        except:
            print('提取邮件信息错误：\n%s' % traceback.format_exc())
            logger.info('提取邮件信息错误：\n%s' % traceback.format_exc())
            return 0
    def get_info(self,r_item,re_id,add_flg):
        # 获取info
        request_var = {
            "var": '<?xml version="1.0"?><object><string name="id">' + r_item + '</string><boolean name="header">true</boolean><boolean name="returnImageInfo">true</boolean><boolean name="returnAntispamInfo">true</boolean><boolean name="autoName">true</boolean><object name="returnHeaders"><string name="Resent-From">A</string><string name="Sender">A</string><string name="List-Unsubscribe">A</string><string name="Reply-To">A</string></object><boolean name="supportTNEF">true</boolean></object>'
        }
        request_urls = "https://mail.163.com/js6/s?sid=" + self.SID + "&func=mbox:readMessage&l=read&action=read"
        r_info = requests.post(url=request_urls, data=request_var, cookies=self.COOKIE)
        # 通过info获取from/to/subject/sentDate
        user_from_data = re.findall('.*<array name="from">\n<string>(.*?)&lt;(.*?)&gt;</string>.*', r_info.text)
        user_to_data = re.findall('.*<array name="to">\n<string>(.*?)&lt;(.*?)&gt;</string>.*', r_info.text)
        if user_from_data:
            user_from = user_from_data[0][0]  # name
            from_email = user_from_data[0][1]  # mail
        else:
            user_from_data = re.findall('.*<array name="from">\n<string>((.*?)@.*)</string>.*', r_info.text)
            user_from = user_from_data[0][1]  # name
            from_email = user_from_data[0][0]  # mail
        if user_to_data:
            user_to = user_to_data[0][0]  # name
            to_email = user_to_data[0][1]  # mail
        else:
            user_to_data = re.findall('.*<array name="to">\n<string>((.*?)@.*)</string>.*', r_info.text)
            user_to = user_to_data[0][1]  # name
            to_email = user_to_data[0][0]  # mail

        subject = re.findall('.*<string name="subject">(.*?)</string>.*', r_info.text)[0]
        sentDate = re.findall('.*<date name="sentDate">(.*?)</date>.*', r_info.text)[0]
        self.eml_data["eml_id"] = re_id
        self.eml_data["user_from"] = user_from.replace(" ", '').replace('\"', '')
        self.eml_data["from_email"] = from_email
        self.eml_data["user_to"] = user_to.replace(" ", '').replace('\"', '')
        self.eml_data["to_email"] = to_email
        self.eml_data["eml_subject"] = subject
        self.eml_data["sentDate"] = sentDate
        # 建立文件夹分类存储
        uf = user_from.replace(" ", '').replace('\"', '')
        eml_path = "Email_download/账号_"+self.email_name + "/" + uf + "/" + sentDate.replace(" ",'_').replace(":","-") + "/"
        # 通过info获取附件信息
        attm = re.findall('.*<string name="id">(\d+?)</string>\n<string name="filename">(.*?)</string>.*', r_info.text)
        # 附件下载地址列表
        eml_attm = []
        attm_text = " "
        if attm:
            if not os.path.exists(self.save_url + eml_path):
                os.makedirs(self.save_url + eml_path)
            for atm_item in attm:
                parts = atm_item[0]
                names = atm_item[1].replace("(", "_").replace(")", "")
                request_attm_url = "https://mail.163.com/js6/read/readdata.jsp?sid=" + self.SID + "&mid=" + r_item + "&part=" + parts + "&mode=download&l=read&action=download_attach"
                #如果覆盖爬取# 当文件存在时删除文件
                rm_file_or_dir(self.save_url + eml_path + names)
                #当文件不存在时下载文件
                if not os.path.isfile(self.save_url + eml_path + names):
                    print("开始下载文件：" +uf+"/"+sentDate+"/"+names)
                    logger.info("开始下载文件：" +uf+"/"+sentDate+"/"+names)
                    # 下载
                    download_result = download.download_from_url(request_attm_url, self.save_url + eml_path + names, self.COOKIE,
                                               self.SID, self.email_name,self.USER_AG)
                    file_url = self.save_url + eml_path
                    name_end = names.split(".")[-1]
                    try:
                        if download_result:
                            if name_end in ("zip", "rar", "tar", "gz"):
                                try:
                                    if name_end == "zip":
                                        file_rep = names.replace(".zip", "")
                                        un_zip(file_url + names, file_url + file_rep)
                                        b_7z_dir(file_url + file_rep, file_url + file_rep)
                                    elif name_end == "rar":
                                        file_rep = names.replace(".rar", "")
                                        un_rar(file_url + names, file_url + file_rep)
                                        b_7z_dir(file_url + file_rep, file_url + file_rep)
                                    elif name_end == "tar":
                                        file_rep = names.replace(".tar", "")
                                        un_tar(file_url + names, file_url + file_rep)
                                        b_7z_dir(file_url + file_rep, file_url + file_rep)
                                    elif name_end == "gz":
                                        file_rep = names.replace(".gz", "")
                                        un_gz(file_url + names, file_url + file_rep)
                                        b_7z_dir(file_url + file_rep, file_url + file_rep)
                                    else:
                                        file_rep = names
                                    if type(attm_text) != str:
                                        attm_text = str(attm_text)
                                    eml_attm.append([file_rep + ".7z", eml_path, attm_text])
                                    rm_file_or_dir(file_url + names)
                                    rm_file_or_dir(file_url + file_rep)
                                except:
                                    eml_attm.append([names, eml_path, attm_text])
                            elif name_end in ("txt", "pdf", "doc", "docx", "pptx", "xls", "xlsx"):
                                if name_end == "txt":
                                    with open(file_url + names, "r") as txt_f:
                                        attm_text = txt_f.read()
                                    txt_f.close()
                                elif name_end == "pdf":
                                    # 利用pdfplumber提取文字
                                    with pdfplumber.open(file_url + names) as pdf:
                                        first_page = pdf.pages[0]
                                        attm_text = first_page.extract_text()
                                elif name_end == "doc":
                                    attm_text = subprocess.check_output(['antiword', file_url + names]).decode("utf-8")
                                elif name_end == "docx":
                                    doc = docx.Document(file_url + names)
                                    attm_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                                elif name_end == "pptx":
                                    presentation = pptx.Presentation(file_url + names)
                                    results = []
                                    for slide in presentation.slides:
                                        for shape in slide.shapes:
                                            if shape.has_text_frame:
                                                for paragraph in shape.text_frame.paragraphs:
                                                    part = []
                                                    for run in paragraph.runs:
                                                        part.append(run.text)
                                                    results.append(''.join(part))
                                    attm_text = [line for line in results if line.strip()]
                                elif name_end in ("xls", "xlsx"):
                                    workbook = open_workbook(file_url + names)  # 打开xls文件
                                    sheet_name = workbook.sheet_names()  # 打印所有sheet名称，是个列表
                                    data = {}
                                    for index, items in enumerate(sheet_name):
                                        sheet = workbook.sheet_by_index(index)  # 根据sheet索引读取sheet中的所有内容
                                        i = 0
                                        while i < sheet.nrows:
                                            data[sheet.col_values(i)[0]] = sheet.col_values(i)
                                            i += 1
                                    attm_text = data
                                if type(attm_text) != str:
                                    attm_text = str(attm_text)
                                eml_attm.append([names, eml_path, attm_text])
                            else:
                                if type(attm_text) != str:
                                    attm_text = str(attm_text)
                                eml_attm.append([names, eml_path, attm_text])
                            print("下载文件完成")
                            logger.info("下载文件完成")
                        else:
                            self.save_flg = 0
                    except:
                        print("download_file_" + names + "error\n%s" % traceback.format_exc())
                        logger.info("download_file_" + names + "error\n%s" % traceback.format_exc())
                        self.save_flg = 0
                    time.sleep(5)
        self.eml_data["eml_attm"] = eml_attm
        # 获取内容
        cont_data = ""
        request_content_url = "https://mail.163.com/js6/read/readhtml.jsp?mid=" + r_item + "&userType=ud&font=15&color=064977"
        r_cont = requests.get(url=request_content_url, cookies=self.COOKIE)
        # 过滤1
        cont_data_filter = re.findall('.*id="content".*\r\n\r\n(.*)\r\n.*', r_cont.text)
        if cont_data_filter:
            cont_data_filter = cont_data_filter[0]
            # 过滤2
            cont_data = remove_tags(cont_data_filter)
        else:
            cont_data_filter2 = re.findall('.*id="content".*\n\n(.*)\n.*', r_cont.text)
            if cont_data_filter2:
                cont_data_filter = cont_data_filter2[0]
                # 过滤2
                cont_data = remove_tags(cont_data_filter)

        self.eml_data["eml_content"] = cont_data.replace("&nbsp;", " ")
        print("提取邮件信息："+uf+"/"+sentDate+" 完成")
        logger.info("提取邮件信息："+uf+"/"+sentDate+" 完成")
        try:
            if self.save_flg:
                self.save_es_data()
                print("保存数据成功")
                logger.info("保存数据成功")
            else:
                print("下载解析错误未保存数据")
                logger.info("下载解析错误未保存数据")
                self.save_flg = 1
            self.eml_data = {}
        except Exception as q:
            print("save_eml_to_es Error:", q)
            logger.info("save_eml_to_es Error:", q)
        time.sleep(2)
    def save_es_data(self):
        esItem = Mail()
        esItem.meta.id = self.eml_data["eml_id"]
        esItem.user_from = self.eml_data["user_from"]
        esItem.from_email = self.eml_data["from_email"]
        esItem.user_to  = self.eml_data["user_to"]
        esItem.to_email = self.eml_data["to_email"]
        esItem.eml_subject  = self.eml_data["eml_subject"]
        esItem.eml_content = self.eml_data["eml_content"]
        esItem.eml_attm = self.eml_data["eml_attm"]
        esItem.sentDate = self.eml_data["sentDate"]
        esItem.eml_id = self.eml_data["eml_id"]
        esItem.save()
if __name__ == '__main__':
    name = "luotao202012"
    passwd = "luotao2020123"
    # idlist = ['414xS2BnhkDFeteF1DZQAAsB', '1071S2maw4DFjSMPC4gAAsg', '458xtbByh8DF0CPYirsgAAsZ', '415xS2BnwgDFetkYTDQAAsS', '269xtbBDQT8FaEBmSvPgAAso', '269xtbBDRoAFaEBo738wABs0', '385xS2BgRQQFc63xUfBQAAsE', '531tbiNQ8AFrPaPdU0AAAsI', '481tbiMAIGFWBwf55PwAAsl', '1631tbioxsAFUMVYrnKQAAsM']
    idlist = []
    a = LoginView(name,passwd,idlist,0)
    a.get_email_list()
