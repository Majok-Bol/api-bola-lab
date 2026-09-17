from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import(
    JWTManager,
    create_access_token,
    set_access_cookies,
    get_jwt_identity,
    unset_jwt_cookies,
    set_refresh_cookies
)
from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()
app=Flask(__name__)
app.config['DATABASE_URL']=os.getenv("DATABASE_URL")
#secret key for signing JWT 
app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
#csrf key
app.config['CSRF_KEY']=os.getenv("CSRF_KEY")
#configure jwt
#where to find jwt token
#store in the cookie
app.config['JWT_TOKEN_LOCATION']=["cookies"]
#name for jwt cookie
app.config['JWT_ACCESS_COOKIE_NAME']="access_token"
#sent cookies only over HTTPS
app.config['JWT_COOKIE_SECURE']=False #set true in production
#enable csrf protection
app.config['JWT_COOKIE_CSRF_PROTECT']=False #set true in production
#prevent js access
app.config['JWT_COOKIE_HTTPONLY']=False #set true in production
#prevent cross origin requests
app.config['JWT_SAMESITE']='Lax' #set Strict in production
#token expiration
#expires after 10 minutes
app.config['JWT_ACCESS_TOKEN_EXPIRES']=timedelta(minutes=10)
#set refresh tokens
app.config['JWT_REFRESH_TOKEN_EXPIRES']=timedelta(minutes=30)
#initialize app with JWT 
jwt=JWTManager()
jwt.init_app(app)

@app.route("/")
def hello():
    return 'Hello world'


if __name__=="__main__":
    app.run(debug=True)