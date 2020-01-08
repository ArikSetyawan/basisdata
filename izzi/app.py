from flask import Flask, render_template, request, redirect, url_for
from peewee import *

db = 'rumahsakit.db'
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta:
		database=database

class dokter(BaseModel):
	id = AutoField(primary_key=True)
	nama = CharField()
	jenis_kelamin = CharField()
	alamat = TextField()
	no_telp = IntegerField()

class perawat(BaseModel):
	id = AutoField(primary_key=True)
	nama = CharField()
	jenis_kelamin = CharField()
	alamat = TextField()
	no_telp = IntegerField()

class pasien(BaseModel):
	id = AutoField(primary_key=True)
	nama = CharField()
	jenis_kelamin = CharField()
	alamat = TextField()
	no_telp = IntegerField()

class obat(BaseModel):
	id = AutoField(primary_key=True)
	nama_obat = CharField()
	exp_date = DateField()
	jenis_obat = CharField()
	jumlah_obat = CharField()

class rekam_medis(BaseModel):
	id = AutoField(primary_key=True)
	id_pasien = ForeignKeyField(pasien)
	id_dokter = ForeignKeyField(dokter)
	id_perawat = ForeignKeyField(perawat)
	penyakit = CharField(null=True)
	tanggal_berobat = DateField()
	list_obat = CharField(null=True)
	ditangani = BooleanField(default=False)

def create_tables():
	with database:
		database.create_tables([dokter,perawat,pasien,obat,rekam_medis])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ini rahasia kita yah'

@app.route('/')
def index():
	jml_antrian = rekam_medis.select().where(rekam_medis.ditangani == False).count()
	return render_template('index.html',jml_antrian=jml_antrian)

@app.route('/dokter',methods=['GET','POST'])
def show_dokter():
	if request.method == 'GET':
		datas = dokter.select()
		return render_template('dokter.html',datas=datas)
	else:
		nama = request.form['nama']
		jenis_kelamin = request.form['jenis_kelamin']
		alamat = request.form['alamat']
		no_telp = request.form['no_telp']
		try:
			dokter.create(
				nama=nama,
				jenis_kelamin=jenis_kelamin,
				alamat=alamat,
				no_telp=no_telp)
			return redirect(url_for('show_dokter'))
		except:
			return redirect(url_for('show_dokter'))

@app.route('/edit_dokter/<id_dokter>',methods=['POST'])
def edit_dokter(id_dokter):
	nama = request.form['nama']
	jenis_kelamin = request.form['jenis_kelamin']
	alamat = request.form['alamat']
	no_telp = request.form['no_telp']
	try:
		d_dokter = dokter.update(
			nama=nama,
			jenis_kelamin=jenis_kelamin,
			alamat=alamat,
			no_telp=no_telp).where(dokter.id == id_dokter)
		d_dokter.execute()
		return redirect(url_for('show_dokter'))
	except:
		return redirect(url_for('show_dokter'))

@app.route('/delete_dokter/<id_dokter>')
def delete_dokter(id_dokter):
	d_dokter = dokter.delete().where(dokter.id == id_dokter)
	d_dokter.execute()
	return redirect(url_for('show_dokter'))
	
@app.route('/perawat',methods=['GET','POST'])
def show_perawat():
	if request.method == 'GET':
		datas = perawat.select()
		return render_template('perawat.html',datas=datas)
	else:
		nama = request.form['nama']
		jenis_kelamin = request.form['jenis_kelamin']
		alamat = request.form['alamat']
		no_telp = request.form['no_telp']
		try:
			perawat.create(
				nama=nama,
				jenis_kelamin=jenis_kelamin,
				alamat=alamat,
				no_telp=no_telp)
			return redirect(url_for('show_perawat'))
		except:
			return redirect(url_for('show_perawat'))

@app.route('/edit_perawat/<id_perawat>',methods=['POST'])
def edit_perawat(id_perawat):
	nama = request.form['nama']
	jenis_kelamin = request.form['jenis_kelamin']
	alamat = request.form['alamat']
	no_telp = request.form['no_telp']
	try:
		d_perawat = perawat.update(
			nama=nama,
			jenis_kelamin=jenis_kelamin,
			alamat=alamat,
			no_telp=no_telp).where(perawat.id == id_perawat)
		d_perawat.execute()
		return redirect(url_for('show_perawat'))
	except:
		return redirect(url_for('show_perawat'))

@app.route('/delete_perawat/<id_perawat>')
def delete_perawat(id_perawat):
	d_perawat = perawat.delete().where(perawat.id == id_perawat)
	d_perawat.execute()
	return redirect(url_for('show_perawat'))

@app.route('/pasien',methods=['GET','POST'])
def show_pasien():
	if request.method == 'GET':
		datas = pasien.select()
		return render_template('pasien.html',datas=datas)
	else:
		nama = request.form['nama']
		jenis_kelamin = request.form['jenis_kelamin']
		alamat = request.form['alamat']
		no_telp = request.form['no_telp']
		try:
			pasien.create(
				nama=nama,
				jenis_kelamin=jenis_kelamin,
				alamat=alamat,
				no_telp=no_telp)
			return redirect(url_for('show_pasien'))
		except:
			return redirect(url_for('show_pasien'))

@app.route('/edit_pasien/<id_pasien>',methods=['POST'])
def edit_pasien(id_pasien):
	nama = request.form['nama']
	jenis_kelamin = request.form['jenis_kelamin']
	alamat = request.form['alamat']
	no_telp = request.form['no_telp']
	try:
		d_pasien = pasien.update(
			nama=nama,
			jenis_kelamin=jenis_kelamin,
			alamat=alamat,
			no_telp=no_telp).where(pasien.id == id_pasien)
		d_pasien.execute()
		return redirect(url_for('show_pasien'))
	except:
		return redirect(url_for('show_pasien'))

@app.route('/rekam_medis_pasien/<id_pasien>')
def rekam_medis_pasien(id_pasien):
	datas = rekam_medis.select().join(dokter).switch(rekam_medis).join(perawat).where(rekam_medis.id_pasien == id_pasien)
	return render_template('rekam_medis_pasien.html',datas=datas)

@app.route('/delete_pasien/<id_pasien>')
def delete_pasien(id_pasien):
	d_pasien = pasien.delete().where(pasien.id == id_pasien)
	d_pasien.execute()
	return redirect(url_for('show_pasien'))


@app.route("/obat",methods=['GET','POST'])
def show_obat():
	if request.method == 'GET':
		datas = obat.select()
		return render_template('obat.html',datas=datas)
	else:
		nama_obat = request.form['nama_obat']
		exp_date = request.form['exp_date']
		jenis_obat = request.form['jenis_obat']
		jumlah_obat = request.form['jumlah_obat']
		try:
			obat.create(
				nama_obat=nama_obat,
				exp_date=exp_date,
				jenis_obat=jenis_obat,
				jumlah_obat=jumlah_obat)
			return redirect(url_for('show_obat'))
		except:
			return redirect(url_for('show_obat'))

@app.route('/edit_obat/<id_obat>',methods=['POST'])
def edit_obat(id_obat):
	nama_obat = request.form['nama_obat']
	exp_date = request.form['exp_date']
	jenis_obat = request.form['jenis_obat']
	jumlah_obat = request.form['jumlah_obat']
	try:
		d_obat = obat.update(
			nama_obat=nama_obat,
			exp_date=exp_date,
			jenis_obat=jenis_obat,
			jumlah_obat=jumlah_obat).where(obat.id == id_obat)
		d_obat.execute()
		return redirect(url_for('show_obat'))
	except:
		return redirect(url_for('show_obat'))

@app.route('/delete_obat/<id_obat>')
def delete_obat(id_obat):
	d_obat = obat.delete().where(obat.id == id_obat)
	d_obat.execute()
	return redirect(url_for('show_obat'))

@app.route('/antrian_pasien',methods=['GET','POST'])
def antrian_pasien():
	if request.method == 'GET':
		datas = rekam_medis.select().where(rekam_medis.ditangani == False)
		return render_template('antrian_pasien.html',datas=datas)
	else:
		id_pasien = request.form['id_pasien']
		id_dokter = request.form['id_dokter']
		id_perawat = request.form['id_perawat']
		tanggal_berobat = request.form['tanggal_berobat']

		try:
			rekam_medis.create(
				id_pasien=id_pasien,
				id_dokter=id_dokter,
				id_perawat=id_perawat,
				tanggal_berobat=tanggal_berobat)
			return redirect(url_for('index'))
		except:
			return redirect(url_for('index'))

@app.route('/tangani_pasien/<id_rekammedis>',methods=['POST'])
def tangani_pasien(id_rekammedis):
	penyakit = request.form['penyakit']
	list_obat = request.form['list_obat']
	# try:
	d_rekammedis = rekam_medis.update(
		penyakit=penyakit,
		list_obat=list_obat,
		ditangani=True).where(rekam_medis.id == id_rekammedis)
	d_rekammedis.execute()
	return redirect(url_for('antrian_pasien'))
	# except:
	# 	return redirect(url_for('antrian_pasien'))

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)