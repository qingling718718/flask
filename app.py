from flask import Flask, request, render_template, session
from flask_sqlalchemy import  SQLAlchemy
from sqlalchemy import and_

import  config
app = Flask(__name__)

app.config.from_object(config)
db = SQLAlchemy(app)
class Simple(db.Model):
    __tablename__ = 'simple'
    id = db.Column(db.Integer ,primary_key=True , autoincrement=True)
    user = db.Column(db.String(100), nullable=False,unique=True)
    pwd = db.Column(db.CHAR(50) , nullable=False ,unique=True)

class Pic(db.Model):
    __tablename__ = 'Pic'
    PicId = db.Column(db.Integer, primary_key=True)
    PicName = db.Column(db.CHAR(50), nullable=False,unique=True)
    Pic = db.Column(db.BLOB)
db.create_all()

@app.route('/lsuccess/', methods=['POST' ,'GET'])
def login():
    if request.method == "POST":
            user = request.form.get('username')
            pwd = request.form.get('password')
            result = Simple.query.filter(and_(Simple.user == user ,Simple.pwd == pwd)).first()
            if result is not None:
                picname= Pic.query.filter.PicName
                return render_template('home.html',picname=picname)
            else:
                return render_template('pserror.html')

def valid_regist(username):
    user = Simple.query.filter(Simple.user == username).first()
    if user:
        return False
    else:
        return True

@app.route('/rsuccess/', methods=['POST' ,'GET'])
def regist():
    error = None
    if request.method == "POST":
            if request.form.get('repwd')== request.form.get('repwd2'):
                if valid_regist(request.form.get('rename')):
                   user = Simple(user=request.form.get('rename'),pwd=request.form.get('repwd'))
                   db.session.add(user)
                   db.session.commit()
                   return render_template('login.html')
                else:
                    error = '该用户名已被注册！'
                    return render_template('regist.html', error=error)
            else:
                error = '两次密码不相同！'
                return render_template('regist.html', error=error)

@app.route('/regist/')
def regist_html():
    return render_template('regist.html')

@app.route('/')
def login_html():
    return render_template('login.html')





if __name__ == '__main__':
    app.run(debug = True)