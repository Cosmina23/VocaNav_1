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
    exist_user = Authentification.query.filter_by(name=name).first()
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


#salvare trasee in baza de date--------------------------------------
class Route(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nume_utilizator = db.Column(db.String(255), nullable=False)
    ziua = db.Column(db.String(20), nullable = False) #ex: luni,marti,..
    data = db.Column(db.Date, nullable = False)
    ora = db.Column(db.Time, nullable = False)

    locatie_start_lat = db.Column(db.Float, nullable=False)
    locatie_start_lng = db.Column(db.Float, nullable=False)
    locatie_end_lat = db.Column(db.Float, nullable=False)
    locatie_end_lng = db.Column(db.Float, nullable=False)

    locatie_start_nume = db.Column(db.String(255), nullable = False)
    locatie_end_nume = db.Column(db.String(255), nullable = False)

    opriri = db.Column(db.Text, nullable = True)

    created_at = db.Column(db.DateTime, default = datetime.datetime.now)

    def __init__(self, ziua, data, ora, locatie_start_lat, locatie_start_lng, locatie_end_lat, locatie_end_lng, locatie_start_nume, locatie_end_nume, opriri, nume_utilizator=None):
        self.ziua = ziua 
        self.data = data 
        self.ora = ora 
        self.locatie_start_lat = locatie_start_lat
        self.locatie_start_lng = locatie_start_lng
        self.locatie_end_lat = locatie_end_lat
        self.locatie_end_lng = locatie_end_lng
        self.locatie_start_nume = locatie_start_nume
        self.locatie_end_nume = locatie_end_nume
        self.opriri = opriri
        self.nume_utilizator = nume_utilizator

class RouteSchema(ma.Schema):
    class Meta:
        fields = (
            'id', 'ziua', 'data', 'ora', 'locatie_start_lat', 'locatie_start_lng', 'locatie_end_lat', 'locatie_end_lng', 'locatie_start_nume', 'locatie_end_nume', 'opriri', 'created_at','nume_utilizator'  
        )

route_schema = RouteSchema()
routes_schema = RouteSchema(many=True)


@app.route('/add_route',  methods=['POST'])
def add_route():
    try:
        data = request.json

        print(f'PRIMIT PE BACKEND:{data}')
    
        route = Route(
            ziua = data['ziua'],
            nume_utilizator = data['nume_utilizator'],
            data = datetime.datetime.strptime(data['data'], '%d.%m.%Y').date(),
            ora = datetime.datetime.strptime(data['ora'], '%H:%M').time(),
            locatie_start_lat = data['locatie_start']['lat'],
            locatie_start_lng = data['locatie_start']['lng'],
            locatie_end_lat = data['locatie_end']['lat'],
            locatie_end_lng = data['locatie_end']['lng'],
            locatie_start_nume = data['locatie_start_nume'],
            locatie_end_nume = data['locatie_end_nume'],
            opriri = str(data.get('opriri', []))
        )

        db.session.add(route)
        db.session.commit()
        return route_schema.jsonify(route)

    except Exception as e:
        print("Eroare salvare traseu:", e)
        return jsonify({"error": str(e)}), 400
    
@app.route('/routes', methods=['GET'])
def get_routes():
    all_routes = Route.query.all()
    return routes_schema.jsonify(all_routes)


#salvare locuri vizitate
class Locuri_Vizitate(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nume_utilizator = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Date, nullable=False)
    lat = db.Column(db.Float, nullable=False, unique=True)
    lng = db.Column(db.Float, nullable=False, unique=True)
    nr_vizite = db.Column(db.Integer, default=1, nullable=False)
    nume_loc = db.Column(db.String(255), nullable=True)

    def __init__(self, data, lat, lng, nr_vizite=1, nume_utilizator=None, nume_loc = None):
        self.data = data
        self.lat = lat
        self.lng = lng
        self.nr_vizite = nr_vizite
        self.nume_utilizator = nume_utilizator
        self.nume_loc = nume_loc


class ViziteSchema(ma.Schema):
    class Meta:
        fields = (
            'data', 'lat', 'lng', 'nr_vizite', 'nume_utilizator', 'nume_loc'
        )


vizita_schema = ViziteSchema()
vizite_schema = ViziteSchema(many=True)


@app.route('/add_vizite',  methods=['POST'])
def add_vizite():
    data = request.json
    lat = data["lat"]
    lng = data["lng"]
    nume_utilizator = data["nume_utilizator"]
    nume_loc = data.get("nume_loc")
    azi = datetime.date.today()
    try:
        # cauta daca locatia exista deja
        locatie = Locuri_Vizitate.query.filter_by(lat=lat, lng=lng).first()

        if locatie:
            locatie.nr_vizite += 1
            locatie.data = azi
            locatie.nume_utilizator = nume_utilizator
            mesaj = "Locație actualizată"
            if nume_loc:
                locatie.nume_loc = nume_loc
        else:
            locatie = Locuri_Vizitate(lat=lat, lng=lng, nr_vizite=1, data=azi,nume_utilizator=nume_utilizator, nume_loc=nume_loc)
            db.session.add(locatie)
            mesaj = "Locație adăugată"

        db.session.commit()
        return jsonify({
            "message": mesaj,
            "lat": lat,
            "lng": lng,
            "nr_vizite": locatie.nr_vizite,
            "nume_utilizator": locatie.nume_utilizator,
            "nume_loc": locatie.nume_loc
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/vizite', methods=['GET'])
def get_vizite():
    nume = request.args.get('nume_utilizator')
    if nume:
        vizite = Locuri_Vizitate.query.filter_by(nume_utilizator=nume).all()
    else:
        vizite = Locuri_Vizitate.query.all()
    return vizite_schema.jsonify(vizite)



if __name__ == "__main__" :
    #with app.app_context():
    #    db.create_all()  # Aceasta creeaza tabelele în baza de date
    app.run(host = '0.0.0.0', port=5000, debug = True)



