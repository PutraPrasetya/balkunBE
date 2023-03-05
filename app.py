from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func, text
from cbr_restaurant import CBR
import mysql.connector

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://zetyaa:12345@localhost:3306/cbr_restoran"

# memanggil database
mydb = mysql.connector.connect(
  host="localhost",
  user="zetyaa",
  password="12345",
  database="cbr_restoran"
)


db = SQLAlchemy(app)
migrate = Migrate(app, db)

class basisKasus(db.Model):
    __tablename__ = 'dataset_restoran'
    No = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nama = db.Column(db.String(38))
    Menu = db.Column(db.String(42))
    Daerah = db.Column(db.String(16))
    Tempat = db.Column(db.String(11))
    Kategori = db.Column(db.String(7))
    Jenis = db.Column(db.String(11))
    Rasa = db.Column(db.String(5))
    Harga = db.Column(db.Integer)
    Rating = db.Column(db.Float)
    Latitude = db.Column(db.Float)
    Longitude = db.Column(db.Float)
    Telepon = db.Column(db.String(14))

class revise(db.Model):
    __tablename__ = 'revise'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Daerah = db.Column(db.String(50))
    Tempat = db.Column(db.String(50))
    Kategori = db.Column(db.String(50))
    Jenis = db.Column(db.String(50))
    Rasa = db.Column(db.String(50))
    Harga = db.Column(db.String(50))
    Rating = db.Column(db.String(50))
    Status = db.Column(db.Integer)

class solutions(db.Model):
    __tablename__ = 'solusi'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_revise = db.Column(db.Integer, db.ForeignKey('revise.ID'))
    No_kasus = db.Column(db.Integer, db.ForeignKey('dataset_restoran.No'))



@app.route('/')
def hello():
    return 'Hello, World!'

# Manggil fungsi CBR
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    daerah = data.get('daerah') 
    tempat = data.get('tempat') 
    kategori = data.get('kategori') 
    jenis = data.get('jenis') 
    rasa = data.get('rasa') 
    harga = data.get('harga') 
    rating = data.get('rating')

    rekomendasi = CBR(mydb, daerah, tempat, kategori, jenis, rasa, harga, rating)

    if rekomendasi is None:
        return jsonify({
            'error' : "Mohon maaf, tidak ada rekomendasi untuk restoran yang anda cari\nMohon menunggu pakar dalam mencari rekomendasi yang sesuai untuk anda",
            'data' : None
        }), 401
    return {"data":rekomendasi}

# Update Revise
@app.route('/submit/revise', methods=['POST'])
def submitRevise():
    data = request.form
    idrevise = data.get('idrevise')
    restoran = data.get('restoran') 
    harga = data.get('harga') 
    rating = data.get('rating')
    latitude = data.get('latitude') 
    longitude = data.get('longitude')
    telepon = data.get('telepon')
    
    submitted = basisKasus(Nama=restoran, Harga=harga, Rating=rating,
                          Latitude=latitude, Longitude=longitude, Telepon=telepon)
    db.session.add(submitted)
    db.session.commit()
    if submitted.No is None:
        return jsonify({
            'error' : "Terjadi Kesalahan",
            'data' : None
        }), 500
    
    solution = solutions(No_kasus=submitted.No, ID_revise=idrevise)
    db.session.add(solution)
    db.session.commit()
    if solution.Id is None:
        return jsonify({
            'error' : "Terjadi Kesalahan",
            'data' : None
        }), 500
    return {"data":'success'}

# Get Revise
@app.route('/revises', methods=['GET'])
def getRevise():
    data = revise.query.all()

    if not data:
        return jsonify({
            'message': 'Tidak ada Revise'
        }), 401
    
    revise_list = []
    for case in data:
        obj = {
            'id': case.ID,
            'daerah': case.Daerah,
            'tempat': case.Tempat,
            'kategori': case.Kategori,
            'jenis': case.Jenis,
            'rasa': case.Rasa,
            'harga': case.Harga,
            'rating': case.Rating,
            'status': case.Status
        }
        revise_list.append(obj)
        
    return jsonify({"data":revise_list})


# Get Solution by Revise
@app.route('/revises/solution', methods=['GET'])
def reviseSolution():
    ID_revise = request.args.get('id_revise')
    data = db.session.execute(
        text("""SELECT * FROM `solusi` LEFT JOIN dataset_restoran ON dataset_restoran.No = solusi.No_kasus WHERE ID_revise = :idrevise;"""),
        {'idrevise': ID_revise}
    )

    solution_list = []
    for revised in data:
        obj = {
            'Id': revised.Id,
            'idRevise': revised.ID_revise,
            'noKasus': revised.No_kasus,
            'nama': revised.Nama,
            'daerah': revised.Daerah,
            'tempat': revised.Tempat,
            'kategori': revised.Kategori,
            'jenis': revised.Jenis,
            'rasa': revised.Rasa,
            'harga': revised.Harga,
            'rating': revised.Rating,
            'latitude': revised.Latitude,
            'longitude': revised.Longitude,
            'telepon': revised.Telepon
        }
        solution_list.append(obj)
        
    return jsonify({"data":solution_list})


if __name__ == '__main__':
    app.run()
