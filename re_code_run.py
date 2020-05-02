from re_code import *
from flask import Flask,request,render_template,redirect,url_for,jsonify,send_from_directory,abort
from yibantest import app
@app.route("/")
def index():
    return render_template('index2.html')
@app.route("/recode",methods=['GET','POST'])
def recode():
    if request.method =="POST":
        return t.clear(request.form['number'])
@app.route("/noform",methods=[ 'GET','POST'])
def noform():
    if request.method =="POST":
        state=t.query(request.form['n_class'])
        if state=="全部签到":
            return "已全部签到"
        elif state=="班级不存在":
            return "班级不存在，请联系管理员查询班级名称"
        else:
            return render_template('result2.html',result_list=dic_name,total=state)
def main():
    global t
    t = LoginPage()
    t.login()
    app.run(host='0.0.0.0', port=5000)
if __name__=="__main__":
    main()
