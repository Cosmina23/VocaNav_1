from flask import Flask, jsonify, request;
from flask_sqlalchemy import SQLAlchemy;
import datetime
import pymysql
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

 
pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/vocanav1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True


db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)

class Authentification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    password = db.Column(db.String(255), nullable = False)


    def __init__(self, name, password):
        self.name = name
        self.password = generate_password_hash(password)
        


class AuthSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'created_at', 'password')

auth_schema = AuthSchema()
auths_schema = AuthSchema(many  =True)



@app.route('/get/<id>/', methods = ['GET'])
def post_details(id):
    account = Authentification.query.get(id)
    return auth_schema.jsonify(account)


@app.route('/get', methods = ['GET'])
def get_accounts():
    all_accounts = Authentification.query.all()
    results = auths_schema.dump(all_accounts)
    return jsonify(results)


@app.route('/check_username', methods = ['POST'])
def check_username():
    name = request.json['name']
    exist_user = Authentification.query.filter_by(name=name).firt()
    if exist_user:
        return jsonify({"available": False})
    return jsonify({"available": True})



@app.route('/add', methods=['POST'])
def add_auth():
    name =  request.json['name']
    password =  request.json['password']

    exist_user = Authentification.query.filter_by(name=name).first()
    if exist_user:
        return jsonify({"message": "Username already taken"}), 400        

    authentification = Authentification(name, password)
    db.session.add(authentification)
    db.session.commit()
    return auth_schema.jsonify(authentification)

@app.route('/login', methods=['POST'])
def login():
    name = request.json['name']
    password = request.json['password']

    user = Authentification.query.filter_by(name=name).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful", "user": user.name}), 200
    else:
        return jsonify({"message":"Invalid username or password"}), 401


@app.route('/update/<id>/', methods = ['PUT'])
def update_account(id):
    account = Authentification.query.get(id)

    name = request.json['name']
    password = request.json['password']
    
    account.name = name
    account.password = password

    db.session.commit()
    return auth_schema.jsonify(account)
    



@app.route('/delete/<id>/', methods = ['DELETE'])
def account_delete(id):
    account = Authentification.query.get(id)
    db.session.delete(account)
    db.session.commit()
    return auth_schema.jsonify(account)



if __name__ == "__main__" :
    #with app.app_context():
    #    db.create_all()  # Aceasta creeaza tabelele în baza de date
    app.run(host = '0.0.0.0', port=5000, debug = True)
