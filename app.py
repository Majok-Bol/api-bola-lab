from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import(
    JWTManager,
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    get_jwt_identity,
    unset_jwt_cookies,
    set_refresh_cookies,
    jwt_required
)
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
load_dotenv()
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
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
#initialize db
db=SQLAlchemy(app)
#initialize app with JWT 
jwt=JWTManager()
jwt.init_app(app)
#initialize app with bcrypt
bcrypt=Bcrypt()
bcrypt.init_app(app)
#initialize app with migrate
migrate=Migrate()
migrate.init_app(app,db)
@app.route("/")
def hello_world():
    return 'Hello world'

#register user
@app.post("/api/v1/auth/register")
def register():
    #get data
    data=request.get_json()
    #check if JSON body is provided
    if not data:
        return jsonify({
            "error":"JSON body required"
        }),400
    #check username
    username=data.get("username")
    #email
    email=data.get("email")
    #password
    password=data.get("password")
    if not username or not email or not password:
        return jsonify({
            "error":"username,email and password are required"
        }),400
    #check if username exists
    username_exists=User.query.filter_by(username=username).first()
       #check if email exists
    email_exists=User.query.filter_by(email=email).first()
    if username_exists or email_exists:
        return jsonify({
            "error":"Invalid username or email"
        }),400
 
   
    #hash password
    hashed_password=bcrypt.generate_password_hash(password).decode("utf-8")
    #save changes to the database
    user=User(username=username,email=email,password=hashed_password)
    db.session.add(user)
    db.session.commit()
    #if everything is correct
    return jsonify({
        "message":"User registered successfully",
        "user":{
            "username":username,
            "email":email,

        }

    }),200
#login user
@app.post("/api/v1/auth/login")
def login():
    data=request.get_json()
    if not data:
        return jsonify({
            "error":"JSON body required"
        }),400
    #username
    username=data.get("username")
    #password
    password=data.get("password")
    #check user in the database
    user=User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password,password):
        return jsonify({
            "error":"Invalid credentials"
        }),401
        
    #if all is correct
    #create access_token
    access_token=create_access_token(identity=str(user.id))
    refresh_token=create_refresh_token(identity=str(user.id))
    response=jsonify({
        "message":"Login successful",
        "username:":user.username
    })

    #put JWT inside cookies
    set_access_cookies(response,access_token)
    set_refresh_cookies(response,refresh_token)
    return response,200
#create note
@app.post("/api/v1/notes")
@jwt_required()
def create_note():
    user_id=get_jwt_identity()
    #get data
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "error":"JSON body required"
        }),400
    #title
    title=data.get("title")
    if not title:
        return jsonify({
            "error":"Title required"
        }),400
    #body
    body=data.get("body")
    if not body:
        return jsonify({
            "error":"Body required"
        }),400
    #save changes to the database
    notes=Notes(title=title,body=body,user_id=user_id)
    db.session.add(notes)
    db.session.commit()
    return jsonify({
        "message":"Note saved successfully",
        "My note":{
            "id":notes.id,
            "title":notes.title,
            "body":notes.body,
            "user_id":notes.user_id
        }
    }),200


#view notes
@app.get("/api/v1/notes/<id>")
@jwt_required()
def get_notes(id):
    # user_id=get_jwt_identity()
    if id:
        try:
            id=int(id)
        except ValueError:
            return jsonify({
                "error":"Id must be an integer"
            }),400


    # Broken Object Level Authorization vulnerability
    # Does not verify that the note belongs to the
    # currently authenticated user
    notes=Notes.query.filter_by(id=id).first()


    # Fix for Broken Object Level Authorization (BOLA)
    # Fetch the note by ID and verify that it belongs
    # to the currently authenticated user
    # notes=Notes.query.filter_by(id=id,user_id=user_id).first()


    if not notes:
        return jsonify({
            "error":"Notes not found"
        }),404
    return jsonify({
        "message":"Saved notes",
        "id":notes.id,
        "title":notes.title,
        "body":notes.body,
        "user_id":notes.user_id
    }),200


 

#logout user
@app.post("/api/v1/auth/logout")
@jwt_required()
def logout():
    response=jsonify({
        "message":"You have been logged out"
    })
    #reset JWT 
    unset_jwt_cookies(response)
    return response,200
#refresh JWT token
@app.post("/api/v1/auth/refresh")
@jwt_required(refresh=True)
def refresh_token():
    user_id=get_jwt_identity()
    new_access_token=create_access_token(identity=str(user_id))
    response=jsonify({
        "message":"Access token refreshed"
    })
    set_access_cookies(response,new_access_token)
    return response,200

#handle JWT errors
#invalid token provided
@jwt.invalid_token_loader
def invalid_token_loader(error):
    return jsonify({
        "error":"Invalid token"
    }),401
#expired token provided
@jwt.expired_token_loader
def expired_token_loader(jwt_header,jwt_payload):
    return jsonify({
        "error":"Token expired"
    }),401
#no token provided
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "error":"Authentication required"
    }),401


#create user model
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(255),nullable=False)
    #notes
    #connect user table to notes table
    notes=db.relationship("Notes",back_populates="author")

#create notes model
class Notes(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    body=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"))
    #owner
    author=db.relationship("User",back_populates="notes")
if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)