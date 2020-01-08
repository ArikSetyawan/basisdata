from flask import Flask, render_template, request, redirect, url_for, session
from peewee import *
import datetime, socket

db = 'tokohp.db'
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta:
		database=database

class level_user(BaseModel):
	id = AutoField(primary_key=True)
	nama_level = CharField(unique=True)
	created_at = DateTimeField()
	modified_at = DateTimeField(null=True)
	active = BooleanField(default=True)

class user(BaseModel):
	id = AutoField(primary_key=True)
	id_level = ForeignKeyField(level_user)
	nama = CharField()
	username = CharField(unique=True)
	password = CharField()

class handphone(BaseModel):
	id = AutoField(primary_key=True)
	tipe_hp = CharField(unique=True)
	harga = IntegerField()
	stok = IntegerField()
	active = BooleanField(default=True)

class transaksi(BaseModel):
	id = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	id_handphone = ForeignKeyField(handphone)
	jumlah_beli = IntegerField()
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
		database.create_tables([level_user,user,handphone,transaksi,log])

def waktu_sekarang():
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	now = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
	return now

def admin():
	if 'loggedin' in session:
		if session['level'] == 1:
			return True
		return False
	return False

def logedin():
	if 'loggedin' in session:
		return True
	return False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ini rahasia kita'

@app.route('/first_access')
def first_access():
	level_user.create(
		nama_level='Admin',
		created_at=waktu_sekarang())
	user.create(
		nama='admin',
		username='admin',
		password='admin',
		id_level=1)
	return 'oke'

@app.route('/',methods=['GET','POST'])
def index():
	if logedin():
		if request.method == 'GET':
			datas = handphone.select().where(handphone.active == True)
			return render_template('index.html',datas=datas)
		else:
			key = request.form['merk']
			d_handphone = handphone.select().where(handphone.tipe_hp.contains(key))
			if d_handphone.exists():
				return render_template('index.html',datas=d_handphone)
			else:
				Pesan = "Tidak Ditemukan"
				return render_template('index.html',Pesan=Pesan)
	return redirect(url_for('login'))

@app.route('/all_level')
def all_level():
	if admin():
		d_level = level_user.select()
		return render_template('all_level.html',datas=d_level)
	return redirect(url_for('index'))

@app.route('/tambah_level',methods=['GET','POST'])
def tambah_level():
	if admin():
		if request.method == 'GET':
			return render_template('tambah_level.html')
		else:
			d_nama_level = request.form['namalevel']
			d_nama_level = d_nama_level.capitalize()
			now = waktu_sekarang()
			try:
				level_user.create(
					nama_level=d_nama_level,
					created_at=now)
				return redirect(url_for('all_level'))
			except:
				return redirect(url_for('tambah_level'))
	return redirect(url_for('index'))

@app.route('/edit_level/<id_level>',methods=['POST'])
def edit_level(id_level):
	if admin():
		d_nama_level = (request.form['namalevel']).capitalize()
		d_active = request.form['active']
		
		if int(d_active) == 1:
			d_active = True
		else:
			d_active = False

		now = waktu_sekarang()
		try:
			d_level = level_user.update(
				nama_level=d_nama_level,
				modified_at=now,
				active = d_active).where(level_user.id == id_level)
			d_level.execute()
			return redirect(url_for('all_level'))
		except:
			return redirect(url_for('all_level'))
	return redirect(url_for('index'))

@app.route('/delete_level/<id_level>')
def delete_level(id_level):
	if admin():
		try:
			d_level = level_user.delete().where(level_user.id == id_level)
			d_level.execute()
			return redirect(url_for('all_level'))
		except:
			return redirect(url_for('all_level'))
	return redirect(url_for('index'))

@app.route('/show_handphone')
def show_handphone():
	if admin():
		handphones = handphone.select()
		return render_template('show_handphone.html',datas=handphones)
	return redirect(url_for('index'))

@app.route('/tambah_handphone',methods=['GET','POST'])
def tambah_handphone():
	if admin():
		if request.method == 'GET':
			return render_template('tambah_handphone.html')
		else:
			d_tipe_hp = request.form['tipe_hp']
			d_harga = request.form['harga']
			d_stock = request.form['stock']
			try:
				handphone.create(
					tipe_hp=d_tipe_hp,
					harga=d_harga,
					stok=d_stock)
				return redirect(url_for('show_handphone'))
			except:
				return redirect(request.url)
	return redirect(url_for('index'))

@app.route('/edit_handphone/<id_handphone>',methods=['POST'])
def edit_handphone(id_handphone):
	if admin():
		d_tipe_hp = request.form['tipe_hp']
		d_harga = request.form['harga']
		d_stock = request.form['stock']
		d_active = request.form['active']
		
		if int(d_active) == 1:
			d_active = True
		else:
			d_active = False
		try:
			d_handphone = handphone.update(
				tipe_hp=d_tipe_hp,
				harga=d_harga,
				stok=d_stock,
				active=d_active).where(handphone.id == id_handphone)
			d_handphone.execute()
			return redirect(url_for('show_handphone'))
		except:
			return redirect(url_for('show_handphone'))
	return redirect(url_for('index'))

@app.route('/delete_handphone/<id_handphone>')
def delete_handphone(id_handphone):
	if admin():
		try:
			d_handphone = handphone.delete().where(handphone.id == id_handphone)
			d_handphone.execute()
			return redirect(url_for('show_handphone'))
		except:
			return redirect(url_for('show_handphone'))
	return redirect(url_for('index'))

@app.route('/beli_handphone/<id_handphone>',methods=['POST'])
def beli_handphone(id_handphone):
	if logedin():
		d_jumlah_beli = request.form['jumlah_beli']
		d_handphone = handphone.get(handphone.id == id_handphone)
		d_total_harga = int(d_jumlah_beli) * int(d_handphone.harga)
		
		jumlahstok = int(d_handphone.stok) - int(d_jumlah_beli)
		if jumlahstok <= 0:
			return redirect(url_for('index'))

		d_handphone_edt = handphone.update(stok=jumlahstok).where(handphone.id == id_handphone)
		d_handphone_edt.execute()

		transaksi.create(
			id_user=session['iduser'],
			id_handphone=id_handphone,
			jumlah_beli = d_jumlah_beli,
			total_harga=d_total_harga,
			waktu_transaksi=waktu_sekarang())
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/login',methods=['GET','POST'])
def login():
	if logedin():
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
					login_at = waktu_sekarang(),
					verified = True)
				return redirect(url_for('index'))
			except:
				log.create(
					username = d_username,
					password = d_password,
					ipaddress = socket.gethostbyname(socket.gethostname()),				
					login_at = waktu_sekarang(),
					verified = False)				
				return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route('/all_karyawan')
def all_karyawan():
	if admin():
		datas = user.select().join(level_user).where(user.id_level > 1)
		levels = level_user.select().where(level_user.active == True)
		return render_template('all_karyawan.html',datas=datas,levels=levels)
	return redirect(url_for('index'))

@app.route('/tambah_karyawan',methods=['GET','POST'])
def tambah_karyawan():
	if admin():
		if request.method == 'GET':
			levels = level_user.select().where(level_user.active == True)
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
	if admin():
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
	if admin():
		try:
			d_user = user.delete().where(user.id == id_karyawan)
			d_user.execute()
			return redirect(url_for('all_karyawan'))
		except:
			return redirect(url_for('all_karyawan'))
	return redirect(url_for('index'))

@app.route('/penjualan')
def penjualan():
	if logedin():
		d_transaksi = transaksi.select().join(user).switch(transaksi).join(handphone)
		return render_template('penjualan.html',datas=d_transaksi)
	return redirect(url_for('index'))

@app.route('/log')
def logs():
	if admin():
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