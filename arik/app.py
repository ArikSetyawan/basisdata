from flask import Flask, render_template, request, redirect, url_for, session
from peewee import *
import datetime, socket

db = 'sembako.db'
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta:
		database=database

class level(BaseModel):
	id = AutoField(primary_key=True)
	nama_level = CharField(unique=True)
	created_at = DateTimeField()
	modified_at = DateTimeField(null=True)
	active = BooleanField(default=True)

class user(BaseModel):
	id = AutoField(primary_key=True)
	id_level = ForeignKeyField(level)
	nama = CharField()
	username = CharField(unique=True)
	password = CharField()

class sembako(BaseModel):
	id = AutoField(primary_key=True)
	merk = CharField(unique=True)
	harga = IntegerField()
	stok = IntegerField()
	active = BooleanField(default=True)

class transaksi(BaseModel):
	id = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	id_sembako = ForeignKeyField(sembako)
	berat = IntegerField()
	total_harga = IntegerField()
	waktu_transaksi = DateTimeField()

class log(BaseModel):
	id = AutoField(primary_key=True)
	username = CharField()
	password = CharField()
	id_user = ForeignKeyField(user,null=True)
	ipaddress = CharField()
	login_at = DateTimeField()
	verified = BooleanField()

def create_tables():
	with database:
		database.create_tables([level,user,sembako,transaksi,log])


# Custom function

def datetimenow():
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	now = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
	return now

def isadmin():
	if 'loggedin' in session:
		if session['level'] == 1:
			return True
		return False
	return False

def islogin():
	if 'loggedin' in session:
		return True
	return False

# End Custom Function


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is a little secret'

@app.route('/',methods=['GET','POST'])
def index():
	if islogin():
		if request.method == 'GET':
			datas = sembako.select().where(sembako.active == True)
			return render_template('index.html',datas=datas)
		else:
			key = request.form['merk']
			d_sembako = sembako.select().where(sembako.merk == key)
			if d_sembako.exists():
				return render_template('index.html',datas=d_sembako)
			else:
				Pesan = "Tidak Ditemukan"
				return render_template('index.html',Pesan=Pesan)
	return redirect(url_for('login'))

@app.route('/all_level')
def all_level():
	if isadmin():
		d_level = level.select()
		return render_template('all_level.html',datas=d_level)
	return redirect(url_for('index'))

# All Level
@app.route('/tambah_level',methods=['GET','POST'])
def tambah_level():
	if isadmin():
		if request.method == 'GET':
			return render_template('tambah_level.html')
		else:
			d_nama_level = request.form['namalevel']
			d_nama_level = d_nama_level.capitalize()
			now = datetimenow()
			try:
				level.create(
					nama_level=d_nama_level,
					created_at=now)
				return redirect(url_for('all_level'))
			except:
				return redirect(url_for('tambah_level'))
	return redirect(url_for('index'))

@app.route('/edit_level/<id_level>',methods=['POST'])
def edit_level(id_level):
	if isadmin():
		d_nama_level = (request.form['namalevel']).capitalize()
		d_active = request.form['active']
		
		if int(d_active) == 1:
			d_active = True
		else:
			d_active = False

		now = datetimenow()
		try:
			d_level = level.update(
				nama_level=d_nama_level,
				modified_at=now,
				active = d_active).where(level.id == id_level)
			d_level.execute()
			return redirect(url_for('all_level'))
		except:
			return redirect(url_for('all_level'))
	return redirect(url_for('index'))

@app.route('/delete_level/<id_level>')
def delete_level(id_level):
	if isadmin():
		try:
			d_level = level.delete().where(level.id == id_level)
			d_level.execute()
			return redirect(url_for('all_level'))
		except:
			return redirect(url_for('all_level'))
	return redirect(url_for('index'))

# End Level

# Start Sembako

@app.route('/show_sembako')
def show_sembako():
	if isadmin():
		sembakos = sembako.select()
		return render_template('show_sembako.html',datas=sembakos)
	return redirect(url_for('index'))


@app.route('/tambah_sembako',methods=['GET','POST'])
def tambah_sembako():
	if isadmin():
		if request.method == 'GET':
			return render_template('tambah_sembako.html')
		else:
			d_merk = request.form['merk']
			d_harga = request.form['harga']
			d_stock = request.form['stock']
			try:
				sembako.create(
					merk=d_merk,
					harga=d_harga,
					stok=d_stock)
				return redirect(url_for('show_sembako'))
			except:
				return redirect(request.url)
	return redirect(url_for('index'))

@app.route('/edit_sembako/<id_sembako>',methods=['POST'])
def edit_sembako(id_sembako):
	if isadmin():
		d_merk = request.form['merk']
		d_harga = request.form['harga']
		d_stock = request.form['stock']
		d_active = request.form['active']
		
		if int(d_active) == 1:
			d_active = True
		else:
			d_active = False
		try:
			d_sembako = sembako.update(
				merk=d_merk,
				harga=d_harga,
				stok=d_stock,
				active=d_active).where(sembako.id == id_sembako)
			d_sembako.execute()
			return redirect(url_for('show_sembako'))
		except:
			return redirect(url_for('show_sembako'))
	return redirect(url_for('index'))

@app.route('/delete_sembako/<id_sembako>')
def delete_sembako(id_sembako):
	if isadmin():
		try:
			d_sembako = sembako.delete().where(sembako.id == id_sembako)
			d_sembako.execute()
			return redirect(url_for('show_sembako'))
		except:
			return redirect(url_for('show_sembako'))
	return redirect(url_for('index'))

@app.route('/beli_sembako/<id_sembako>',methods=['POST'])
def beli_sembako(id_sembako):
	if islogin():
		d_berat = request.form['berat']
		d_sembako = sembako.get(sembako.id == id_sembako)
		d_total_harga = int(d_berat) * int(d_sembako.harga)
		
		jumlahstok = int(d_sembako.stok) - int(d_berat)
		if jumlahstok <= 0:
			return redirect(url_for('index'))

		d_sembako_edt = sembako.update(stok=jumlahstok).where(sembako.id == id_sembako)
		d_sembako_edt.execute()

		transaksi.create(
			id_user=session['iduser'],
			id_sembako=id_sembako,
			berat = d_berat,
			total_harga=d_total_harga,
			waktu_transaksi=datetimenow())
		return redirect(url_for('index'))
	return redirect(url_for('index'))
# End Sembako

@app.route('/login',methods=['GET','POST'])
def login():
	if islogin():
		return redirect(url_for('index'))
	else:
		if request.method == 'GET':
			return render_template('login.html')
		else:
			d_username = request.form['username']
			d_password = request.form['password']

			try:
				d_user = user.get((user.username == d_username)&(user.password==d_password))
				session['loggedin'] = True
				session['iduser'] = int(d_user.id)
				session['level'] = int(str(d_user.id_level))

				log.create(
					username = d_username,
					password = d_password,
					id_user = d_user.id,
					ipaddress = socket.gethostbyname(socket.gethostname()),				
					login_at = datetimenow(),
					verified = True)
				return redirect(url_for('index'))
			except:
				log.create(
					username = d_username,
					password = d_password,
					ipaddress = socket.gethostbyname(socket.gethostname()),				
					login_at = datetimenow(),
					verified = False)				
				return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route('/all_karyawan')
def all_karyawan():
	if isadmin():
		datas = user.select().join(level).where(user.id_level > 1)
		levels = level.select().where(level.active == True)
		return render_template('all_karyawan.html',datas=datas,levels=levels)
	return redirect(url_for('index'))

@app.route('/tambah_karyawan',methods=['GET','POST'])
def tambah_karyawan():
	if isadmin():
		if request.method == 'GET':
			levels = level.select().where(level.active == True)
			return render_template('tambah_karyawan.html',levels=levels)
		else:
			d_id_level = request.form['level']
			d_nama = request.form['nama']
			d_username = request.form['username']
			d_password = request.form['password']

			try:
				user.create(
					id_level=d_id_level,
					nama=d_nama,
					username=d_username,
					password=d_password)
				return redirect(url_for('all_karyawan'))
			except:
				return redirect(request.url)
	return redirect(url_for('index'))

@app.route('/edit_karyawan/<id_karyawan>',methods=['POST'])
def edit_karyawan(id_karyawan):
	if isadmin():
		d_id_level = request.form['level']
		d_nama = request.form['nama']
		d_username = request.form['username']
		d_password = request.form['password']

		try:
			d_user = user.update(
				id_level=d_id_level,
				nama = d_nama,
				username=d_username,
				password=d_password).where(user.id==id_karyawan)
			d_user.execute()
			return redirect(url_for('all_karyawan'))
		except:
			return redirect(url_for('all_karyawan'))
	return redirect(url_for('index'))

@app.route('/delete_karyawan/<id_karyawan>')
def delete_karyawan(id_karyawan):
	if isadmin():
		try:
			d_user = user.delete().where(user.id == id_karyawan)
			d_user.execute()
			return redirect(url_for('all_karyawan'))
		except:
			return redirect(url_for('all_karyawan'))
	return redirect(url_for('index'))

@app.route('/penjualan')
def penjualan():
	if islogin():
		d_transaksi = transaksi.select().join(user).switch(transaksi).join(sembako)
		return render_template('penjualan.html',datas=d_transaksi)
	return redirect(url_for('index'))

@app.route('/log')
def logs():
	if isadmin():
		d_log = log.select()
		d_user = user.select()
		lis_log = []
		for data in d_log:
			d = {}
			d['id'] = data.id
			d['username'] = data.username
			d['password'] = data.password
			for i in d_user:
				if data.id_user == None:
					d['user'] = 'Unknow'
				elif int(str(i.id)) == int(str(data.id_user)):
					d['user'] = i.nama
					break
				else:
					d['user'] = 'Unknow'
			d['login_at'] = data.login_at
			d['ipaddress'] = data.ipaddress
			d['verified'] = data.verified
			lis_log.append(d)
		return render_template('log.html',log=lis_log)
	return redirect(url_for('index'))

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)