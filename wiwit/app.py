from flask import Flask, render_template, request, redirect, url_for, session
from peewee import *
import datetime, socket, time
from datetimerange import DateTimeRange

db = 'futsal.db'
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

class lapangan(BaseModel):
	id = AutoField(primary_key=True)
	kelas = CharField(unique=True)
	nama_lapangan = CharField(unique=True)
	harga = IntegerField()
	active = BooleanField(default=True)

class transaksi(BaseModel):
	id = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	id_lapangan = ForeignKeyField(lapangan)
	nama_pemesan = CharField()
	no_ktp = IntegerField()
	checkin = DateTimeField()
	checkout = DateTimeField()
	total_harga = IntegerField()
	waktu_transaksi = DateTimeField()
	selesai = BooleanField(default=False)

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
		database.create_tables([level,user,lapangan,transaksi,log])

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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/first_access')
def first_access():
	try:
		level.create(
			nama_level="Admin",
			created_at=datetimenow())
		user.create(
			id_level=1,
			nama="admin",
			username='admin',
			password='admin')
		return "Created"
	except:
		return "already"

@app.route('/',methods=['GET','POST'])
def index():
	if islogin():
		if request.method == 'GET':
			datas = lapangan.select().where(lapangan.active == True)
			return render_template('index.html',datas=datas)
		else:
			key = request.form['nama_lapangan']
			d_lapangan = lapangan.select().where(lapangan.nama_lapangan == key)
			if d_lapangan.exists():
				return render_template('index.html',datas=d_lapangan)
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

@app.route('/show_lapangan')
def show_lapangan():
	if isadmin():
		lapangans = lapangan.select()
		return render_template('show_lapangan.html',datas=lapangans)
	return redirect(url_for('index'))


@app.route('/tambah_lapangan',methods=['GET','POST'])
def tambah_lapangan():
	if isadmin():
		if request.method == 'GET':
			return render_template('tambah_lapangan.html')
		else:
			d_nama_lapangan = request.form['nama_lapangan']
			d_harga = request.form['harga']
			d_kelas = request.form['kelas']
			try:
				lapangan.create(
					nama_lapangan=d_nama_lapangan,
					harga=d_harga,
					kelas=d_kelas)
				return redirect(url_for('show_lapangan'))
			except:
				return redirect(request.url)
	return redirect(url_for('index'))

@app.route('/edit_lapangan/<id_lapangan>',methods=['POST'])
def edit_lapangan(id_lapangan):
	if isadmin():
		d_nama_lapangan = request.form['nama_lapangan']
		d_harga = request.form['harga']
		d_kelas = request.form['kelas']
		d_active = request.form['active']
		
		if int(d_active) == 1:
			d_active = True
		else:
			d_active = False
		try:
			d_lapangan = lapangan.update(
				nama_lapangan=d_nama_lapangan,
				harga=d_harga,
				kelas=d_kelas,
				active=d_active).where(lapangan.id == id_lapangan)
			d_lapangan.execute()
			return redirect(url_for('show_lapangan'))
		except:
			return redirect(url_for('show_lapangan'))
	return redirect(url_for('index'))

@app.route('/delete_lapangan/<id_lapangan>')
def delete_lapangan(id_lapangan):
	if isadmin():
		try:
			d_lapangan = lapangan.delete().where(lapangan.id == id_lapangan)
			d_lapangan.execute()
			return redirect(url_for('show_lapangan'))
		except:
			return redirect(url_for('show_lapangan'))
	return redirect(url_for('index'))

@app.route('/beli_lapangan/<id_lapangan>',methods=['POST'])
def beli_lapangan(id_lapangan):
	if islogin():
		status = True
		d_checkin = request.form['checkin']
		d_checkout = request.form['checkout']
		d_waktuin = request.form['waktuin']
		d_waktuout = request.form['waktuout']
		d_lapangan = lapangan.get(lapangan.id == id_lapangan)
		d_nama = request.form['nama']
		d_ktp = request.form['ktp']

		d_checkin = datetime.datetime.strptime(d_checkin,'%Y-%m-%d')
		d_checkout = datetime.datetime.strptime(d_checkout,'%Y-%m-%d')
		d_waktuin = datetime.datetime.strptime(d_waktuin,'%H:%M')
		d_waktuout = datetime.datetime.strptime(d_waktuout,'%H:%M')
		d_checkin = datetime.datetime(d_checkin.year,d_checkin.month,d_checkin.day,d_waktuin.hour,d_waktuin.minute)
		d_checkout = datetime.datetime(d_checkout.year,d_checkout.month,d_checkout.day,d_waktuout.hour,d_waktuout.minute)

		# cek
		d_transaksi = transaksi.select().where((transaksi.selesai == False)&(transaksi.id_lapangan == id_lapangan))
		if d_transaksi.exists():
			for data in d_transaksi:
				d_checkin_d = datetime.datetime(data.checkin.year,data.checkin.month,data.checkin.day,data.checkin.hour,data.checkin.minute)
				d_checkout_d = datetime.datetime(data.checkout.year,data.checkout.month,data.checkout.day,data.checkout.hour,data.checkout.minute)

				checkin_now = d_checkin
				checkout_now = d_checkout
				
				time_range = DateTimeRange(checkin_now,checkout_now)
				for date in time_range.range(datetime.timedelta(days=1)):
					hour_range = DateTimeRange(date,checkout_now)
					for hour in hour_range.range(datetime.timedelta(hours=1)):
						minute_range = DateTimeRange(hour,checkout_now)
						for minute in hour_range.range(datetime.timedelta(minutes=1)):
							if d_checkin_d == minute or d_checkout_d == minute:
								# print(True)
								status = False
								break
		if status == True:
			lama_menginap = d_checkout - d_checkin
			# print(lama_menginap.seconds // 3600) #getHours
			d_total_harga = int(lama_menginap.seconds // 3600) * int(d_lapangan.harga)

			transaksi.create(
				id_user=session['iduser'],
				id_lapangan=id_lapangan,
				nama_pemesan=d_nama,
				no_ktp=d_ktp,
				checkin = d_checkin,
				checkout = d_checkout,
				total_harga=d_total_harga,
				waktu_transaksi=datetimenow())
			return redirect(url_for('index'))
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/confirm_lapangan/<id_trx>')
def confirm_lapangan(id_trx):
	if islogin():
		d_transaksi = transaksi.update(selesai=True).where(transaksi.id == id_trx)
		d_transaksi.execute()
		return redirect(url_for('penjualan'))
	return redirect(url_for('index'))

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
		d_transaksi = transaksi.select().join(user).switch(transaksi).join(lapangan)
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