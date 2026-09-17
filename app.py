from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import(
    create_access_token,
    set_access_cookies,
    get_jwt_identity,
    unset_jwt_cookies,
    set_refresh_cookies
)
from dotenv import load_dotenv
import os
load_dotenv()
app=Flask(__name__)
dbs=app.config['DATABASE_URL']=os.getenv("DATABASE_URL")
print("Database url: ",dbs)
@app.route("/")
def hello():
    return 'Hello world'


if __name__=="__main__":
    app.run(debug=True)