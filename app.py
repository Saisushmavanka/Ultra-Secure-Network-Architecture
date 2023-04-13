from flask import Flask,render_template,redirect,request,session
import time
from pymongo import MongoClient
from cryptography.fernet import Fernet
from datetime import datetime

key = Fernet.generate_key()
fernet = Fernet(key)

client=MongoClient('localhost',27017)
db=client['C15']
c=db['register']
c1=db['data']

app=Flask(__name__)
app.secret_key='c15sacet'

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['username']=None
    return redirect('/')

@app.route('/registeruser',methods=['post','get'])
def registerUser():
    name=request.form['name']
    mobileno=request.form['mobileno']
    emailid=request.form['emailid']
    password=request.form['password']
    print(name,mobileno,emailid,password)
    k={}
    k['name']=name
    k['mobileno']=mobileno
    k['emailid']=emailid
    k['password']=password
    c.insert_one(k)
    return render_template('register.html',res='Registered Successfully')

@app.route('/loginuser',methods=['post','get'])
def loginUser():
    mobileno=request.form['mobileno']
    password=request.form['password']
    print(mobileno,password)
    for i in c.find():
        if(i['mobileno']==mobileno and i['password']==password):
            session['username']=mobileno
            return redirect('/dashboard')
    return render_template('login.html',err='Invalid login')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/insertdata',methods=['post'])
def insertdata():
    data=request.form['data']
    print(data)
    encMessage = fernet.encrypt(data.encode())
    decMessage = fernet.decrypt(encMessage).decode()
    k={}
    k['user']=session['username']
    k['inputdata']=data
    k['encodeddata']=encMessage
    k['decodeddata']=decMessage
    k['timestamp']=str(datetime.now())
    c1.insert_one(k)
    return render_template('dashboard.html',res='Data Protected on the Network')

@app.route('/viewdata')
def viewdata():
    data=[]
    for i in c1.find():
        if(i['user']==session['username']):
            dummy=[]
            dummy.append(i['inputdata'])
            dummy.append(i['encodeddata'])
            dummy.append(i['decodeddata'])
            dummy.append(i['timestamp'])
            data.append(dummy)
    return render_template('viewdata.html',dashboard_data=data,len=len(data))


if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0',port=5001)
