from django.shortcuts import render, HttpResponse, redirect
from elasticsearch import Elasticsearch
import json,time
import traceback
from mailListVew.LoginView import LoginView
import os,re
from .models import spider_user,super_user
from django.core.paginator import Paginator
from mailListVew.xzip import rm_file_or_dir,un_zip,un_7z,un_gz,un_rar,un_tar,b_7z
# Create your views here.
client = Elasticsearch(hosts=["127.0.0.1"])

filter_user = ""
search_data = {}
def toindex(request):
    try:
        if 'user' not in request.session:
            return redirect("/index/1")
    except Exception as e:
        print("login_error")
        return render(request, 'login.html')
    return redirect("/index/1")
#首页
def index(request,pindex):
    global filter_user,search_data,search
    try:
        try:
            if 'user' not in request.session:
                return render(request, 'login.html')
        except Exception as e:
            print("login_error")
            return render(request, 'login.html')
        search ={}
        mail_user = spider_user.objects.all()
        if not search_data:#没有search_data
            if not filter_user :
                search = {"match_all": {} }
            else:
                search = {
                        "term": {
                            "user_to":filter_user
                        }
                    }
        else:
            if filter_user:#有search_data 有 filter_user是一个嵌套查询
                search = {
                    "bool":{
                        "should":[
                            {
                                "term": {
                                    "user_to": filter_user
                                }
                            },
                            {
                            search_data
                            }
                        ]
                    }
                }
            else:
                search = search_data

        response = client.search(
            index="mail163",
            body={
                "query": search,
                "from": 0,
                "size": 10000,
            }
        )
        hit_list = []
        for hit in response["hits"]["hits"]:
            from collections import defaultdict
            hit_dict = defaultdict(str)
            hit_dict["user_from"] = hit["_source"]["user_from"]
            hit_dict["from_email"] = hit["_source"]["from_email"]
            hit_dict["user_to"] = hit["_source"]["user_to"]
            hit_dict["to_email"] = hit["_source"]["to_email"]
            hit_dict["eml_subject"] = hit["_source"]["eml_subject"]
            hit_dict["eml_content"] = hit["_source"]["eml_content"]
            if "eml_attm" in hit["_source"]:
                hit_dict["eml_attm"] = hit["_source"]["eml_attm"]
                for item in hit["_source"]["eml_attm"]:
                    if item[0].split(".")[-1] in ("bmp","png","tif","gif","jpeg","jpg","webp"):
                        item.append("imgflg")
                    elif item[0].split(".")[-1] in ("zip","rar","gz","bz2", "xz","tar","7z"):
                        item.append("zipflg")
                    elif item[0].split(".")[-1] in ("txt","pdf","doc","docx","ppt","pptx","xls","xlsx"):
                        item.append("textflg")
                    else:
                        item.append("nullflg")
            else:
                hit_dict["eml_attm"] = []
            hit_dict["sentDate"] = hit["_source"]["sentDate"].replace(" ",'_')
            hit_dict["eml_id"] = hit["_source"]["eml_id"]
            hit_list.append(hit_dict)

    except Exception as e:
        print(e)
        hit_list = []
        mail_user=[]
    if pindex == "":  # django中默认返回空值，所以加以判断，并设置默认值为1
        pindex = 1
    else:  # 如果有返回在值，把返回值转为整数型
        int(pindex)
    paginator = Paginator(hit_list, 10)
    page = paginator.page(pindex)
    return render(request, 'index.html',{"all_hits": page,"mail_user":mail_user,"filter_user":filter_user})

#展示选定用户的搜索
def select_user(request):
    global filter_user
    try:
        user_data = request.POST
        filter_user = user_data["name"]
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

#搜索
def search(request):
    global search_data
    try:
        data = request.POST
        content = data["content"]
        sent = data["sent"]
        subject = data["subject"]
        attm = data["attm"]
        if sent:#发件人检索
            search_data ={
                "match":{
                    "from_email":sent
                }
            }
        elif subject:#主题检索
            search_data = {
                "match": {
                    "eml_subject": subject
                }
            }
        elif attm:#附件检索  附件名/附件文本
            search_data = {
                "match": {
                    "eml_attm": attm
                }
            }
        elif content:#全文检索
            search_data = {
                "multi_match":{
                    "query":content,
                    "fields":["from_email", "to_email","eml_subject","eml_content","eml_attm"]
                }
            }
        else:
            search_data = {}
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

#进入启动爬虫页面，显示可用爬虫用户
def start_spider(request):
    try:
        if 'user' not in request.session:
            return render(request, 'login.html')
    except Exception as e:
        print("login_error")
        return render(request, 'login.html')
    mal = spider_user.objects.all()
    return render(request, 'start_spider.html', {"mal":mal})

#进入爬虫用户管理，显示所有用户
def show_user(request):
    mail = spider_user.objects.all()
    return render(request, 'spider_user.html', {"mal":mail})

#修改用户
def edit_user(request,uid):
    try:
        user_data = request.POST
        name = user_data["name"]
        passwd = user_data["passwd"]
        mail = spider_user.objects.filter(id=uid)
        mail.name = str(name)
        mail.passwd = str(passwd)
        mail.update()
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))
#添加用户
def add_user(request):
    try:
        user_data = request.POST
        name = user_data["name"]
        passwd = user_data["passwd"]
        mail = spider_user()
        if not spider_user.objects.filter(name = name).exists():
            mail.name = str(name)
            mail.passwd = str(passwd)
            mail.save()
            ret = {"code": 1, "msg": "ok"}
        else:
            ret = {"code": 0, "msg": "用户已存在"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

#删除用户
def del_user(request, uid):
    try:
        spider_user.objects.filter(id=uid).delete()
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

#启动爬虫
def run_spider(request):
    try:
        user_data = request.POST
        name = user_data["name"]
        passwd = user_data["passwd"]
        add_flg = int(user_data["add_flg"])
        #查询所有id，可选覆盖或增量爬虫
        # 1增量爬取，0覆盖爬取
        try:
            response = client.search(
                index="mail163",
                body={
                    "stored_fields": ["eml_id"],
                    "query": {
                        "match_all": {}
                    },
                    "from": 0,
                    "size": 10000,
                }
            )
            id_list = []
            if response:
                for hit in response["hits"]["hits"]:
                    id_list.append(hit["_id"])
            login_class = LoginView(name, passwd, id_list, add_flg)
        except:
            id_list = []
            login_class = LoginView(name, passwd, id_list, add_flg)
        login_class.start_spider()
        ret = {"code": 1,"msg":"ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))
file_context = {}

#打开一个未识别分类的文件
def open_file(request):
    global file_context
    try:
        data = request.POST
        file_url = data["file_url"]
        file_name = data["file_name"]
        save_url = os.path.dirname(os.path.dirname(__file__))
        f = open(save_url+file_url+file_name,"r")
        file_data = f.read()
        file_context = {"code":1,"file_data": file_data, "file_name": file_name}
    except Exception as e:
        file_context = {"code": 0, "file_data": str(e), "file_name": "404"}
    return HttpResponse(json.dumps(file_context))

#进入未识别文件内容页面
def file(request):
    global file_context
    try:
        if 'user' not in request.session:
            return render(request, 'login.html')
    except Exception as e:
        print("login_error")
        return render(request, 'login.html')
    return render(request, 'file.html',file_context)


#用户登录网站
def login(request):
    return render(request, 'login.html')

def do_login(request):
    login_data = request.POST
    name = login_data["name"]
    pwd = login_data["passwd"]
    print("name:"+name,"passwd:"+pwd)
    lg = super_user.objects.filter(name=name)
    if lg.exists():
        if lg.values().first()["passwd"] == pwd:
            request.session['user'] = name
            ret = {"code": 1, "msg": ""}
            return HttpResponse(json.dumps(ret))
        else:
            ret = {"code": 0, "msg": "用户名或密码输入有误"}
            return HttpResponse(json.dumps(ret))
    else:
        ret = {"code": 0, "msg": "用户名或密码输入有误"}
        return HttpResponse(json.dumps(ret))

def logout(request):
    request.session.flush()
    return render(request, 'login.html')

#进入爬虫用户管理，显示所有用户
def show_supuser(request):
    try:
        if 'user' not in request.session:
            return render(request, 'login.html')
    except Exception as e:
        print("login_error")
        return render(request, 'login.html')
    mail = super_user.objects.all()
    return render(request, 'super_user.html', {"mal":mail})

#修改用户
def edit_supuser(request,uid):
    try:
        user_data = request.POST
        passwd = user_data["passwd"]
        sup = super_user.objects.filter(id=uid)
        sup.passwd = str(passwd)
        sup.update()
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))
#添加用户
def add_supuser(request):
    try:
        user_data = request.POST
        name = user_data["name"]
        passwd = user_data["passwd"]
        sup = super_user()
        if not super_user.objects.filter(name=name).exists():
            sup.name = str(name)
            sup.passwd = str(passwd)
            sup.user_grade = 2
            sup.save()
            ret = {"code": 1, "msg": "ok"}
        else:
            ret = {"code": 0, "msg": "用户已存在"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

#删除用户
def del_supuser(request, uid):
    try:
        super_user.objects.filter(id=uid).delete()
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))


def openfile_url(request):
    try:
        user_data = request.POST
        file_url = os.path.dirname(os.path.dirname(__file__))+user_data["file_url"]
        os.popen('dde-file-manager ' + file_url)
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

def xzip_open(request):
    try:
        user_data = request.POST
        file_url = os.path.dirname(os.path.dirname(__file__))+user_data["file_url"]
        file_name = user_data["file_name"]
        file_rep = ""
        ret = {"code": 1, "msg": "ok"}
        if file_name.split(".")[-1] == "zip":
            file_rep = file_name.replace(".zip","").replace("(","").replace(")","")
            un_zip(file_url+file_name,file_url+file_rep)
        elif file_name.split(".")[-1] == "rar":
            file_rep = file_name.replace(".rar", "").replace("(","").replace(")","")
            un_rar(file_url + file_name, file_url + file_rep)
        elif file_name.split(".")[-1] == "tar":
            file_rep = file_name.replace(".tar", "").replace("(","").replace(")","")
            un_tar(file_url + file_name, file_url + file_rep)
        elif file_name.split(".")[-1] == "gz":
            file_rep = file_name.replace(".gz", "").replace("(","").replace(")","")
            un_gz(file_url + file_name, file_url + file_rep)
        elif file_name.split(".")[-1] == "7z":
            file_rep = file_name.replace(".7z", "").replace("(","").replace(")","")
            un_7z(file_url + file_name, file_url + file_rep)
        else:
            ret = {"code": 0, "msg": "暂不支持解压"}
        os.popen('dde-file-manager ' + file_url + file_rep)
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))

def clean_data(request):
    global filter_user
    try:
        data = request.POST
        filter_users = data["filter_user"]
        os_url = os.path.dirname(os.path.dirname(__file__))
        save_url = os_url + "/static/email_data/Email_download"  # +数据文件
        query_data = {}
        if filter_users:
            save_url = save_url+"/账号_"+filter_users
            query_data = {'user_to': filter_users}
            filter_user = ""
        query = {'query': {'match': query_data}}
        client.delete_by_query(index='mail163', body=query, doc_type='email_data')
        rm_file_or_dir(save_url)
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))
def del_this(request):
    try:
        get_data = request.POST
        ml_id = get_data["data_id"]
        client.delete(index='mail163', doc_type='email_data', id=ml_id)
        user_from = get_data["user_from"]
        sent_Date = get_data["sent_Date"]
        os_url = os.path.dirname(os.path.dirname(__file__))
        save_url = os_url + "/static/email_data/Email_download/"
        rm_file_or_dir(save_url+user_from+"/"+sent_Date)
        time.sleep(1)
        ret = {"code": 1, "msg": "ok"}
    except Exception as e:
        print('7zordocument.format_exc():\n%s' % traceback.format_exc())
        ret = {"code": 0, "msg": str(e)}
    return HttpResponse(json.dumps(ret))