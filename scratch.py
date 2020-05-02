#coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import xlwt
import os,re,time,datetime,sys,shutil
from flask import Flask,request,render_template
from yibantest import app
from escape import Escape
is_empty=True
pos='这些放表格的存储路径'
def save_in_excel(dic_name,file_name):
	workbook=xlwt.Workbook(encoding='utf-8')
	worksheet=workbook.add_sheet('My Worksheet')
	i=0
	for key,value in dic_name.items():
		worksheet.write(i,0,label=key)
		worksheet.write(i,1,label=str(value))
		i=i+1
		#表格保存路径
	global pos
	if not os.path.exists(pos):
		os.makedirs(pos)
	workbook.save(pos+str(file_name)+'.xls')
def compare_time(time1,time2):
    s_time = time.mktime(time.strptime(time1,'%Y-%m-%d'))
    e_time = time.mktime(time.strptime(time2,'%Y-%m-%d'))
    return int(s_time) - int(e_time)
class LoginPage(object):
    def __init__(self):
        #创建一个参数对象，用来控制chrome以无界面的方式打开
        chrome_options = Options()
        #不加载图片,加快访问速度
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        #无界面，后面的两个是固定写法 必须这么写
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
    def get_imgcode(self):
        '''获取验证码的src'''
        return self.driver.find_element_by_id("imageY").get_attribute("src")
    def login(self):
        '''模拟登录'''
        self.driver.get("https://mp.yiban.cn/login/index")
        self.driver.find_element_by_id("account").send_keys(u"这里是管理平台账号")
        self.driver.find_element_by_id("password").send_keys(u"这里是管理平台密码")
        self.driver.find_element_by_id("loginSubmit").click()
        time.sleep(1.5)
        if self.driver.title!="公共帐号管理平台 | 发送消息":
            return False
            # yzm=input()
            # self.driver.find_element_by_id("inputyzm").send_keys(yzm)
            # self.driver.find_element_by_id("loginSubmit").click()
        #点开微社区，不点开的话无法访问之后的页面
        self.switch_wei()
        return True
        #设置等待时间,等待登录成功进入页面
        #time.sleep(5)
        # self.driver.save_screenshot("page/yiban2.png")
    def yz(self,yzm):
        self.driver.find_element_by_id("inputyzm").send_keys(yzm)
        self.driver.find_element_by_id("loginSubmit").click()
        time.sleep(1.5)
        if self.driver.title=="公共帐号管理平台 | 发送消息":
            #点开微社区，不点开的话无法访问之后的页面
            self.switch_wei()
            return True
        else:
            return False
    def switch_wei(self):
        self.driver.find_element_by_id("menu_manage").click()
        self.driver.find_element_by_id("mainPage").click()
        self.driver.switch_to_frame("iframepage")
        self.driver.find_element_by_id("forum").click()
    def getHTMLText(self,url):
        '''获取页面信息'''
        global is_empty
        while True:
            if is_empty==True:
                is_empty=False
                js = "window.open('"+url+"');"
                self.driver.execute_script(js)
                windows = self.driver.window_handles
                self.driver.switch_to.window(windows[-1])
                html=self.driver.page_source
                self.driver.close()
                self.driver.switch_to.window(windows[0])
                is_empty=True
                return html
def main():
    url="http://www.yiban.cn/manage/forum/index"
    t = LoginPage()
    t.login()
    start_date="2019-11-30"
    end_date="2019-11-30"
    outside_time={}
    dic_name={'测试人员':0}
    current_date=" "
    page=1
    while True:
        url_page=url+"?page="+str(page)
        time="-"
        html=t.getHTMLText(url_page)
        print(html)
        soup=BeautifulSoup(html,'html.parser')
        tbody=soup.find('tbody')
        tr = tbody.find_all('tr')
        file_name=start_date+"---"+end_date
        for i in tr:
            try:
                td=i.find_all('td')
                key=td[1].text.split(" ")[0]
                #更新当前日期
                if td[  4].text.split(" ")[0]!=current_date:
                    current_date=td[4].text.split(" ")[0]
                    if compare_time(td[4].text.split(" ")[0],end_date)<=0 and compare_time(td[4].text.split(" ")[0],start_date)>=0:
                        print("当前时间："+current_date)
                if compare_time(td[4].text.split(" ")[0],end_date)<=0 and compare_time(td[4].text.split(" ")[0],start_date)>=0:
                    if key in dic_name:
                        if key in outside_time:
                            if outside_time[key]==td[4].text.split(" ")[0]:
                                continue
                            else:
                                dic_name[key]=dic_name[key]+1
                                outside_time[key]=td[4].text.split(" ")[0]
                        else:
                            outside_time[key]=td[4].text.split(" ")[0]
                            dic_name[key]=dic_name[key]+1
                    continue
                elif compare_time(td[4].text.split(" ")[0],start_date)<0:
                    save_in_excel(dic_name,file_name)
                    return
                else:
                    continue
            except:
                continue
        page=page+1
if __name__ == "__main__":
    main()
