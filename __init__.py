from flask import Flask,redirect,url_for,render_template,session,request
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,EqualTo
from werkzeug import secure_filename
import random
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app=Flask(__name__)
app.config['SECRET_KEY']="ASKLDFGOK"
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/new' 
app.config['RECAPTCHA_PUBLIC_KEY']='6LdS7dIUAAAAAPDHXYMdUxdh9uJuxWntO-TtLfNM'
app.config['RECAPTCHA_PRIVATE_KEY']='6LdS7dIUAAAAAK_qOvwGWi52tJ7TBWcez4g9508f'
app.config['UPLOAD_FOLDER']='static'

db=SQLAlchemy(app)
admin=Admin(app)

class Registeration(FlaskForm):
	username=StringField("Username",validators=[DataRequired(),Length(min=5,max=10)])
	email=StringField("Email",validators=[DataRequired(),Email()])
	password=PasswordField("Password",validators=[DataRequired()])
	confirmpass=PasswordField("Confirm Password",validators=[DataRequired(),EqualTo('password')])
	recaptcha=RecaptchaField()
	submit=SubmitField('Register')


class Login(FlaskForm):
	email=StringField("Email",validators=[DataRequired(),Email()])
	password=PasswordField("Password",validators=[DataRequired(),Length(min=5,max=10)])
	remember=BooleanField("Remember me")
	submit=SubmitField('Sign Up')



class User(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	email=db.Column(db.String(20),nullable=False)
	password=db.Column(db.String(20),nullable=False)
	profile=db.Column(db.String(40),nullable=False,default='download.jfif')
	stream=db.Column(db.String(30),nullable=False)
	posts=db.relationship('Post',backref='author',lazy=True)



class Post(db.Model):
	#__searchable__=['content']
	id=db.Column(db.Integer,primary_key=True)
	content=db.Column(db.String(200),nullable=False)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

#whoosh_index(app,Post)

admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Post,db.session))

@app.route("/register",methods=['POST','GET'])
def register():
	form=Registeration()
	if request.method=='POST':
			username=request.form['username']
			email=request.form['email']
			password=request.form['password']
			entry=User(email=email,password=password)
			db.session.add(entry)
			db.session.commit()			
	return render_template("register.html",form=form)



@app.route("/home",methods=['POST','GET'])
def home():
	if "user1" in session:
		user=session['user1']
		name=User.query.filter_by(email=user).first()
		return render_template("home1.html",post=name.posts)
	else:
		return redirect(url_for('login'))



@app.route("/",methods=['POST','GET'])
def login():
	form=Login()
	if request.method=='POST':
		email=request.form['email'] 
		user=User.query.filter_by(email=email).first()
		if user:
			if user.password==form.password.data:
				session['user1']=user.email
				return redirect(url_for("home"))
			else:
				return redirect(url_for("login"))
	return render_template("login.html",form=form)



@app.route("/logout")
def logout():
	if "user1" in session:
		session.pop("user1",None)
		return redirect(url_for('login'))
	else:
		return redirect(url_for('login'))


@app.route("/edit/<string:id>",methods=['POST','GET'])
def edit(id):
	if "user1" in session:
		if request.method=='POST':
			name=Post.query.filter_by(id=id).first()
			name.content=request.form['textarea']
			db.session.commit()
			return redirect(url_for("home"))

		return render_template("edit.html",id=id)


@app.route("/delete/<string:id>",methods=['POST','GET'])
def delete(id):
	if "user1" in session:
		name=Post.query.filter_by(id=id).first()
		db.session.delete(name)
		db.session.commit()
		return redirect(url_for("home"))



@app.route("/addpost",methods=['POST','GET'])
def addpost():
	if "user1" in session:
		if request.method=='POST':
			user=session['user1']
			email=User.query.filter_by(email=user).first()
			entry=request.form['textarea']
			add=Post(content=entry,author=email)
			db.session.add(add)
			db.session.commit()
			return redirect(url_for("home"))

		else:
			return render_template("addpost.html")	



@app.route("/submit",methods=['POST','GET'])
def submit():
	if "user1"in session:
		search=request.form['search']
		return f"{search}"	



@app.route("/profile",methods=['POST','GET'])
def profile():
	if "user1" in session:
		user=session['user1']
		email=User.query.filter_by(email=user).first()
		if request.method=='POST':
			user=session['user1']
			email=User.query.filter_by(email=user).first()
			stream1=request.form['stream']
			email.stream=stream1
			db.session.commit()
		return render_template("profile.html",user=email)



@app.route("/updatepic",methods=['POST','GET'])
def update():
	if "user1" in session:
		user=session['user1']
		email=User.query.filter_by(email=user).first()
		if request.method=='POST':
			f=request.files['photos']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
			user=session['user1']
			email=User.query.filter_by(email=user).first()
			email.profile=f.filename
			db.session.commit()

		return render_template('profile.html',user=email)	



if __name__ == '__main__':
	db.create_all()
	app.run(debug=True,port=5749)