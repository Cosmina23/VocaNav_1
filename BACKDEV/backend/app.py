from flask import Flask, jsonify, request;
from flask_sqlalchemy import SQLAlchemy;
import datetime
import pymysql
from flask_marshmallow import Marshmallow
 
pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/vocanav1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True


db = SQLAlchemy(app)
ma = Marshmallow(app)

class Authentification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    phone = db.Column(db.String(15), unique = True, nullable = False)
    voice_hash = db.Column(db.String(255), nullable = False)


    def __init__(self, name, phone, voice_hash):
        self.name = name
        self.phone = phone
        self.voice_hash = voice_hash
        


class AuthSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'created_at', 'phone', 'voice_hash')

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




@app.route('/add', methods=['POST'])
def add_auth():
    name =  request.json['name']
    phone =  request.json['phone']
    voice_hash =  request.json['voice_hash']

    authentification = Authentification(name, phone, voice_hash)
    db.session.add(authentification)
    db.session.commit()
    return auth_schema.jsonify(authentification)

@app.route('/update/<id>/', methods = ['PUT'])
def update_account(id):
    account = Authentification.query.get(id)

    name = request.json['name']
    phone = request.json['phone']
    
    account.name = name
    account.phone = phone

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
    #    db.create_all()  # Aceasta creează tabelele în baza de date
    app.run(host = '192.168.1.4', port=5000, debug = True)

