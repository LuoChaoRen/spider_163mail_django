import requests
from lxml import etree
from fake_useragent import UserAgent

import MySQLdb
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="mail163", charset="utf8")
cursor = conn.cursor()
ua = UserAgent()
def crawl_ips():
    headers = {"User-Agent":ua.random}
    for i in range(1,35):
        re = requests.get("https://www.kuaidaili.com/free/inha/{0}".format(i), headers=headers)
        html = etree.HTML(re.text)
        all_trs = html.xpath("//div[@id='list']//tbody/tr")
        for tr in all_trs:
            all_texts = tr.xpath("td/text()")
            print(all_texts)
            speed = "99"
            speed_str = all_texts[5]
            if speed_str:
                speed = speed_str.split("秒")[0]

            proxy = all_texts[0]+":"+ all_texts[1]
            proxy_type = str(all_texts[3])

            print("判断ip是否可用")
            http_url = "http://www.baidu.com"
            proxy_url = "http://{0}".format(proxy)
            print(proxy_url)
            try:
                proxy_dict = {
                    "http": proxy_url,
                }
                print("start")
                response = requests.get(http_url, proxies=proxy_dict)
                print("stop")
            except Exception as e:
                print("invalid ip and port")
            else:
                code = response.status_code
                if code >= 200 and code < 300:
                    print("effective ip")
                    sql = "insert spider_proxy(proxy, speed, proxy_type) VALUES('{0}', '{1}', '{2}')".format(proxy, speed,proxy_type)
                    cursor.execute(sql)
                    conn.commit()
                else:
                    print("invalid ip and port")
    print("ok")


class GetIP(object):
    def delete_ip(self, proxy):
        #从数据库中删除无效的ip
        print("删除无效的ip")
        delete_sql = """delete from spider_proxy_s where proxy='{0}'""".format(proxy)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, proxy):
        #判断ip是否可用
        print("判断ip是否可用")
        http_url = "http://www.baidu.com"
        proxy_url1 = "http://{0}".format(proxy)
        proxy_url2 = "https://{0}".format(proxy)
        print(proxy_url1)
        try:
            proxy_dict = {
                "http":proxy_url1,
                "https": proxy_url2,
            }
            print("start")
            response = requests.get(http_url, proxies=proxy_dict)
            print("stop")
        except Exception as e:
            print ("invalid ip and port")
            self.delete_ip(proxy)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print ("effective ip")
                return True
            else:
                print  ("invalid ip and port")
                self.delete_ip(proxy)
                return False

    def get_random_ip(self):
        print("get_ip")
        #从数据库中随机获取一个可用的ip
        random_sql = """
              SELECT proxy FROM spider_proxy_s
            ORDER BY RAND()
            LIMIT 1
            """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            proxy = ip_info[0]

            judge_re = self.judge_ip(proxy)
            if judge_re:
                return "http://{0}".format(proxy)
            else:
                return self.get_random_ip()



# print (crawl_ips())
if __name__ == "__main__":
    # get_ip = GetIP()
    # get_ip.get_random_ip()
    crawl_ips()