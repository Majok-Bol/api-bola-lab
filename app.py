from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import(
    create_access_token,
    set_access_cookies,
    get_jwt_identity,
    unset_jwt_cookies,
    set_refresh_cookies
)
app=Flask(__name__)
@app.route("/")
def hello():
    return 'Hello world'


if __name__=="__main__":
    app.run(debug=True)