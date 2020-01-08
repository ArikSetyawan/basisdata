from flask import Flask, render_template, request, redirect, url_for, session
from peewee import *
import datetime, socket, time
from datetimerange import DateTimeRange

db = 'londri.db'
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

class jenis_londri(BaseModel):
	id = AutoField(primary_key=True)
	nama_londri = CharField(unique=True)
	harga = IntegerField()
	created_at = DateTimeField()
	active = BooleanField(default=True)

class transaksi(BaseModel):
	id = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	id_jenis_londri = ForeignKeyField(jenis_londri)
	nama_pemesan = CharField()
	no_telp = IntegerField()
	berat = IntegerField()
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
		database.create_tables([level,user,jenis_londri,transaksi,log])

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

@app.route('/',methods=['GET'])
def index():
	if islogin():
		return redirect(url_for('londrian'))
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

@app.route('/show_jenis_londri')
def show_jenis_londri():
	if isadmin():
		jenis_londris = jenis_londri.select()
		return render_template('show_jenis_londri.html',datas=jenis_londris)
	return redirect(url_for('index'))


@app.route('/tambah_jenis_londri',methods=['GET','POST'])
def tambah_jenis_londri():
	if isadmin():
		if request.method == 'GET':
			return render_template('tambah_jenis_londri.html')
		else:
			d_nama_jenis_londri = request.form['nama_jenis_londri']
			d_harga = request.form['harga']
			try:
				jenis_londri.create(
					nama_londri=d_nama_jenis_londri,
					harga=d_harga,
					created_at=datetimenow())
				return redirect(url_for('show_jenis_londri'))
			except:
				return redirect(request.url)
	return redirect(url_for('index'))

@app.route('/edit_jenis_londri/<id_jenis_londri>',methods=['POST'])
def edit_jenis_londri(id_jenis_londri):
	if isadmin():
		d_nama_jenis_londri = request.form['nama_jenis_londri']
		d_harga = request.form['harga']
		d_active = request.form['active']
		
		if int(d_active) == 1:
			d_active = True
		else:
			d_active = False
		try:
			d_jenis_londri = jenis_londri.update(
				nama_londri=d_nama_jenis_londri,
				harga=d_harga,
				active=d_active).where(jenis_londri.id == id_jenis_londri)
			d_jenis_londri.execute()
			return redirect(url_for('show_jenis_londri'))
		except:
			return redirect(url_for('show_jenis_londri'))
	return redirect(url_for('index'))

@app.route('/delete_jenis_londri/<id_jenis_londri>')
def delete_jenis_londri(id_jenis_londri):
	if isadmin():
		try:
			d_jenis_londri = jenis_londri.delete().where(jenis_londri.id == id_jenis_londri)
			d_jenis_londri.execute()
			return redirect(url_for('show_jenis_londri'))
		except:
			return redirect(url_for('show_jenis_londri'))
	return redirect(url_for('index'))

@app.route('/tambah_londrian',methods=['POST'])
def tambah_londrian():
	if islogin():
		d_nama = request.form['nama']
		d_notelp = request.form['notelp']
		berat = request.form['berat']
		d_jenis_londri = request.form['jenis_londri']
		try:
			d_jenis_londri = jenis_londri.get(jenis_londri.id == d_jenis_londri)
			total_harga = int(berat) * int(d_jenis_londri.harga)
			transaksi.create(
				id_user=session['iduser'],
				id_jenis_londri=d_jenis_londri.id,
				nama_pemesan=d_nama,
				no_telp=d_notelp,
				berat = int(berat),
				total_harga=total_harga,
				waktu_transaksi=datetimenow())
			return redirect(url_for('index'))
		except:
			return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/confirm_selesai_londri/<id_trx>')
def confirm_jenis_londri(id_trx):
	if islogin():
		d_transaksi = transaksi.update(selesai=True).where(transaksi.id == id_trx)
		d_transaksi.execute()
		return redirect(url_for('londrian'))
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

@app.route('/londrian')
def londrian():
	if islogin():
		d_jenis_londri = jenis_londri.select()
		d_transaksi = transaksi.select().join(user).switch(transaksi).join(jenis_londri)
		return render_template('londrian.html',datas=d_transaksi,jenis_londri=jenis_londri)
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