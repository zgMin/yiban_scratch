#coding=utf-8
from flask import Flask,request,render_template,redirect,url_for,jsonify,send_from_directory,abort
from yibantest import app
from escape import Escape
from scratch import *
url="http://www.yiban.cn/manage/forum/index"
current_date=" "
file_name=""
invalid=False
page=1
yz_error=False
outside_time={}
dic_name={'测试人员':0}
def init():
    '''数据初始化'''
    global  current_date,page,yz_error,outside_time,dic_name
    current_date=" "
    yz_error=False
    outside_time={}
    page=1
    for i in dic_name:
        dic_name[i]=0
@app.route("/")
def index():
    '''首页，判断是进入登陆页面还是查询页面'''
    if is_yz is False:
        global imgcode
        imgcode=t.get_imgcode()
        return redirect(url_for('login'))
    else:
        return redirect(url_for('date_page'))
@app.route("/date",methods=['GET','POST'])
def date_page():
    '''查询日期页面'''
    if is_yz is True:
        # print(request.method)
        if request.method == "GET":
            return render_template('date.html')
        if request.method =="POST":
            start_date=request.form['start_date']
            end_date=request.form['end_date']
            # print(start_date,end_date)
            global page,dic_name,url,current_date,outside_time,file_name
            not_ok=True
            init()  #每次查询前进行初始化，以便于进行多次查询
            while not_ok:
                url_page=url+"?page="+str(page)
                html=t.getHTMLText(url_page)
                # print(html)
                soup=BeautifulSoup(html,'html.parser')
                title_text=soup.find('title')
                # print(title_text)
                if title_text=="<title>警告！</title>":
                    main()
                    if is_yz==True:
                        continue
                    else:
                        global  invalid
                        invalid=True
                        return redirect(url_for('index'))
                tbody=soup.find('tbody')
                tr = tbody.find_all('tr')
                file_name=start_date+"---"+end_date
                for i in tr:
                    try:
                        td=i.find_all('td')
                        key=td[1].text.split(" ")[0]
                        #更新当前日期
                        if td[4].text.split(" ")[0]!=current_date:
                            current_date=td[4].text.split(" ")[0]
                            # if compare_time(td[4].text.split(" ")[0],end_date)<=0 and compare_time(td[4].text.split(" ")[0],start_date)>=0:
                            #     print("当前时间："+current_date)
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
                            not_ok=False
                        else:
                            continue
                    except:
                        continue
                page=page+1
            # print('ok')
            return redirect(url_for('result'))
    else:
        return redirect(url_for('index'))
@app.route("/login",methods=['GET','POST'])
def login():
    '''验证登录页面'''
    global is_yz,yz_error,invalid
    # GET请求
    if request.method == "GET":
        return render_template("login.html",imgdata=imgcode,yz_error=yz_error,invalid=invalid)
    # POST请求
    if request.method == "POST":
        invalid=False
        if t.yz(request.form['inputyzm']) is True:
            is_yz=True
            yz_error=False
            return redirect(url_for('date_page'))
        else:
            yz_error=True
            return redirect(url_for('index'))
@app.route("/result",methods=['GET','POST'])
def result():
    '''用于展示结果，提供下载接口'''
    # print(request.method)
    if request.method=="POST":
        save_in_excel(dic_name,file_name)   #需要下载的话再生成excel表格
        return redirect(url_for('download'))
    return render_template('result.html',result_list=dic_name)
@app.route("/download")
def download():
    '''下载excel表格'''
    return send_from_directory(pos,filename=str(file_name)+'.xls',as_attachment=True)
@app.route("/clear",methods=['GET','POST'])
def clear():
    '''用于清除已保存的exel表格'''
    if os.path.exists(pos):
        shutil.rmtree(pos)
        return "ok"
    else:
        return "当前无缓存，无需清理"
# @app.route('/user/<username>')
# def show_user_profile(username):
#     # show the user profile for that user
#     return 'User %s' % Escape(username)
def main():
    global t
    t = LoginPage()
    global is_yz
    is_yz=t.login()
    # print(is_yz)
    app.run(host='0.0.0.0', port=5000)
if __name__=="__main__":
    main()

