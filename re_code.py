import time,re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.chrome.options import Options
from flask import Flask,request,render_template,redirect,url_for,jsonify,send_from_directory,abort
is_empty=True
dic_name={}
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
    def login(self):
        self.driver.get("https://u.uyiban.com/#/login")
        self.driver.find_element_by_id("mobile").send_keys(u"校本化账号")
        self.driver.find_element_by_id("password").send_keys(u"校本化密码")
        self.driver.find_element_by_tag_name("button").click()
        time.sleep(1.5)
        self.driver.find_element_by_xpath("//*[text()='设备管理']").click()
    def clear(self,number):
        global is_empty
        while True:
            if is_empty==True:
                is_empty=False
                self.driver.get("https://app.uyiban.com/devicemanagement/admin/#/home")
                self.driver.find_element_by_id("Number").clear()
                self.driver.find_element_by_id("Number").send_keys(number)
                self.driver.find_element_by_tag_name("button").click()
                try:
                    time.sleep(1.5)
                    self.driver.find_elements_by_xpath("//*[text()='清除识别码']")[1].click()
                    time.sleep(1.5)
                    self.driver.find_elements_by_tag_name("button")[5].click()
                    is_empty=True
                    print(number)
                    return "清除成功，请重新授权"
                except:
                    is_empty=True
                    return "当前未授权或清除失败，请重新尝试"
    def query(self,n_class):
        global is_empty,cnt,dic_name
        while True:
            if is_empty==True:
                cnt=0
                dic_name.clear()
                is_empty=False
                self.driver.get("https://app.uyiban.com/nightattendance/admin/#/roster")
                self.driver.find_element_by_id("SignInState").click()
                self.driver.find_element_by_xpath("//*[text()='未签到']").click()
                self.driver.find_element_by_xpath("//input[@placeholder='机构搜索']").clear()
                self.driver.find_element_by_xpath("//input[@placeholder='机构搜索']").send_keys(n_class)
                self.driver.find_element_by_xpath("//input[@placeholder='机构搜索']").send_keys(Keys.ENTER)
                time.sleep(1.5)
                try:
                    self.driver.find_element_by_xpath("//div[@title='%s']"%n_class).click()
                    time.sleep(2.5)
                    self.driver.find_element_by_tag_name("button").click()
                except:
                    is_empty=True
                    return "班级不存在"
                while True:
                    try:
                        time.sleep(2.5)
                        html=self.driver.page_source
                        soup=BeautifulSoup(html,'html.parser')
                        tbody=soup.find('tbody')
                        tr = tbody.find_all('tr')
                        for i in tr:
                            cnt=cnt+1
                            td=i.find_all('td')
                            a=re.search('<div>(.*?)</div>',str(td[0])).group(1)
                            #td[1]是被折叠的学号，需要改进
                            dic_name[a]=td[1]
                        next=self.driver.find_element_by_xpath("//li[@title='下一页']")
                        if(next.get_attribute("aria-disabled")=="false"):
                            next.click()
                            continue
                        else:
                            is_empty=True
                            print(cnt)
                            # for i in dic_name:
                            #     print(i)
                            #     print(dic_name[i])
                            return cnt
                    except:
                        is_empty=True
                        return "全部签到"


# t = LoginPage()
# t.login()
# t.query("2019化学类班")
# print(cnt)
