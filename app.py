from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_mysqldb import MySQL
import datetime
import pdfkit
import smtplib
from email.mime.text import MIMEText

app= Flask(__name__)
app.config

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '5248'
app.config['MYSQL_DB'] = 'mydb'
mysql = MySQL(app)

app.secret_key = "mysecretkey"

def send_email(to, subject, body):
    # Set up SMTP connection
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'andrewclinica@gmail.com'  # your email address
    smtp_password = 'pokggrymlewjwbux'  # your email password
    smtp_conn = smtplib.SMTP(smtp_server, smtp_port)
    smtp_conn.starttls()
    smtp_conn.login(smtp_username, smtp_password)

    # Create email message
    msg = MIMEText(body)
    msg['To'] = to
    msg['From'] = smtp_username
    msg['Subject'] = subject

    # Send email
    smtp_conn.sendmail(smtp_username, to, msg.as_string())
    smtp_conn.quit()


def get_cita_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute("""
SELECT citas.id_c, pacientes.nombre AS paciente_nombre, medicos.nombre_m AS medico_nombre, citas.fecha, citas.correo, citas.motivo, citas.creado, citas.tipo
FROM citas
INNER JOIN pacientes ON citas.paciente_id = pacientes.id
INNER JOIN medicos ON citas.medico_id = medicos.id_m
    
        WHERE citas.id_c = %s
    """, (id,))
    cita = cur.fetchone()
    return cita



def get_patient_by_id(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
    patient = cursor.fetchone()
    return patient

@app.route('/generate_pdf/<int:id>', methods=['POST'])
def generate_pdf(id):
    patient = get_patient_by_id(id)
    html = render_template('paciente_info.html', paciente=patient)
    pdf = pdfkit.from_string(html, False, options={"enable-local-file-access": ""})
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=paciente_{id}.pdf'
    return response

@app.route('/generate_pdf_cita/<int:id>', methods=['POST'])
def generate_pdf_cita(id):
    cita = get_cita_by_id(id)
    html = render_template('cita_info.html', cita=cita)
    pdf = pdfkit.from_string(html, False, options={"enable-local-file-access": ""})
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=cita_{id}.pdf'
    return response


@app.route('/list_citas')
def list_citas():
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT citas.id_c, pacientes.nombre AS paciente_nombre, medicos.nombre_m AS medico_nombre, citas.fecha, citas.correo, citas.motivo, citas.creado, citas.tipo
    FROM citas
    INNER JOIN pacientes ON citas.paciente_id = pacientes.id
    INNER JOIN medicos ON citas.medico_id = medicos.id_m
    """)
    citas = cur.fetchall()
    cur.close()
    return render_template('list_citas.html', citas=citas)



@app.route('/pacientes')
def list_pacientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM pacientes')
    pacientes = cur.fetchall()
    cur.close()
    return render_template('list_pacientes.html', pacientes=pacientes)

@app.route('/pacientes/add', methods=['GET', 'POST'])
def add_pacientes():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido_pat = request.form['apellido_pat']
        apellido_mat = request.form['apellido_mat']
        correo = request.form['correo']
        password = request.form['password']
        telefono = request.form['telefono']
        cuidad = request.form['cuidad']
        sexo = request.form['sexo']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO pacientes (nombre, apellido_pat, apellido_mat, correo, password, telefono, cuidad, sexo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
         (nombre, apellido_pat, apellido_mat, correo, password, telefono, cuidad, sexo))
        mysql.connection.commit()
        cur.close()
        flash('Paciente se ha agregado correctamente!')
        return redirect(url_for('list_pacientes'))
    return render_template('add_pacientes.html')

@app.route('/pacientes/edit/<int:id>', methods=['GET', 'POST'])
def edit_paciente(id):
    patient = get_patient_by_id(id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido_pat = request.form['apellido_pat']
        apellido_mat = request.form['apellido_mat']
        correo = request.form['correo']
        telefono = request.form['telefono']
        cuidad = request.form['cuidad']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE pacientes SET nombre = %s, apellido_pat = %s, apellido_mat = %s, correo = %s, telefono = %s, cuidad = %s WHERE id = %s",
        (nombre, apellido_pat, apellido_mat, correo, telefono, cuidad, id))
        mysql.connection.commit()
        flash('Paciente se ha modificado correctamente!')
        return redirect(url_for('list_pacientes'))
    return render_template('edit_paciente.html', patient=patient)

@app.route('/pacientes/delete/<int:id>', methods=['POST'])
def delete_paciente(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM citas WHERE paciente_id = %s', (id,))
    cur.execute('DELETE FROM pacientes WHERE id = %s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('list_pacientes'))

@app.route('/dashboard.html')
def dashboard():
    if 'correo' in session:
        correo = session['correo']
        cur = mysql.connection.cursor()
        cur.execute('SELECT nombre FROM pacientes WHERE correo=%s', (correo,))
        record = cur.fetchone()
        if record:
            nombre = record[0]
            return render_template('dashboard.html', correo=correo, nombre=nombre)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'correo' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template("index.html")

@app.route('/citas.html')
def citas():
    today = datetime.datetime.now().date()
    return render_template("citas.html", today=today)

@app.route('/contactos.html')   
def contactos():
    return render_template("contactos.html")

@app.route('/inicio.html', methods=['GET','POST'])
def inicio():
    return render_template("inicio.html")

@app.route('/logout.html', methods=['GET','POST'])
def logout():
    session.pop('correo', None)
    return redirect(url_for('index'))

@app.route('/add_medico.html', methods=['POST'])
def add_medico():
    if request.method == "POST":
        nombre_m = request.form["nombre_m"]
        apellido_pat_m = request.form["apellido_pat_m"]
        apellido_mat_m = request.form["apellido_mat_m"]
        especialidad_m = request.form["especialidad_m"]
        telefono_m = request.form["telefono_m"]
        ciudad_m = request.form["ciudad_m"]
        email_m = request.form["email_m"]
        password_m = request.form["password_m"]
        cur = mysql.connection.cursor()
        
        # Para ver si ya esta registrado el correo
        cur.execute("SELECT email_m FROM medicos WHERE email_m=%s", (email_m,))
        result = cur.fetchone()
        if result:
            flash("Este correo ya esta registrado.")
            return redirect(url_for("registro_medico"))

        # agrega el nuevo usuario
        cur.execute("INSERT INTO medicos (nombre_m, apellido_pat_m, apellido_mat_m, especialidad_m, telefono_m, ciudad_m, email_m, password_m) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (nombre_m, apellido_pat_m, apellido_mat_m, especialidad_m, telefono_m, ciudad_m, email_m, password_m))
        mysql.connection.commit()
        flash("La cuenta se creo con exito!")
        return redirect(url_for("inicio_medico"))

@app.route('/generar_cita', methods=['POST'])
def generar_cita():
    # retrieve form data
    correo = request.form['correo']
    fecha = request.form['date']
    motivo = request.form['motivo']
    tipo = request.form['tipo']
    cur = mysql.connection.cursor()
    
    # saca id desde la tabla pacientes usando el correo como id
    cur.execute("SELECT id FROM pacientes WHERE correo=%s", (correo,))
    result = cur.fetchone()
    if result is None:
        flash("El correo no se encuentra registrado en nuestra base de datos")
        return redirect(url_for("citas"))
    paciente_id = result[0]
    
    # saca id desde la tabla medicos usando el especailidad como id
    cur.execute("SELECT id_m FROM medicos WHERE especialidad_m=%s", (tipo,))
    result = cur.fetchone()
    medico_id = result[0]
    
    # insert appointment data into appointments table
    cur.execute("INSERT INTO citas (paciente_id, medico_id, fecha, correo, motivo, tipo) VALUES (%s, %s, %s, %s, %s, %s)",
    (paciente_id, medico_id, fecha, correo, motivo, tipo))
    mysql.connection.commit()

    # send email to patient
    cur.execute("SELECT nombre FROM pacientes WHERE id=%s", (paciente_id,))
    nombre = cur.fetchone()[0]
    cur.execute("SELECT nombre_m FROM medicos WHERE id_m=%s", (medico_id,))
    nombre_m = cur.fetchone()[0]

    subject = 'Cita Agendada'
    body = f'Buenos dias {nombre} ! Tu cita para el {fecha} ha sido agendada con el doctor {nombre_m} en el area de {tipo}. Gracias por usar nuestro servicio.'
    send_email(correo, subject, body)
    flash("La cita se creo con exito!")
    return redirect(url_for("citas"))



@app.route('/add.html', methods=['POST'])
def add():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido_pat = request.form["apellido_pat"]
        apellido_mat = request.form["apellido_mat"]
        correo = request.form["correo"]
        password = request.form["password"]
        telefono = request.form["telefono"]
        cuidad = request.form["cuidad"]
        sexo = request.form["sexo"]
        cur = mysql.connection.cursor()
        
        # Para ver si ya esta registrado el correo
        cur.execute("SELECT correo FROM pacientes WHERE correo=%s", (correo,))
        result = cur.fetchone()
        if result:
            flash("Este correo ya esta registrado.")
            return redirect(url_for("registro"))

        # agrega el nuevo usuario
        cur.execute("INSERT INTO pacientes (nombre, apellido_pat, apellido_mat, correo, password, telefono, cuidad, sexo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (nombre, apellido_pat, apellido_mat, correo, password, telefono, cuidad, sexo))
        mysql.connection.commit()
        flash("La cuenta se creo con exito!")
        return redirect(url_for("inicio"))

@app.route('/login_medico.html', methods=['GET','POST'])
def login_medico():
    if request.method == "POST":
        email_m = request.form.get("email_m")
        password_m = request.form.get("password_m")
        if email_m and password_m:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM medicos WHERE email_m=%s AND password_m=%s', (email_m,password_m))
            record = cur.fetchone()
            if record:
                session['loggedin'] = True
                session['correo'] = email_m
                session['nombre'] = record[0] 
                return redirect(url_for("dashboard_medico"))
            else:
                flash("Correo o Password Invalidos!")
        else:
            flash("Correo o Password Invalidos!")
    return redirect(url_for("inicio_medico"))

@app.route('/dashboard_medico.html')
def dashboard_medico():
    if 'correo' in session:
        email_m = session['correo']
        cur = mysql.connection.cursor()
        cur.execute('SELECT nombre_m FROM medicos WHERE email_m=%s', (email_m,))
        record = cur.fetchone()
        if record:
            nombre = record[0]
            return render_template('dashboard_medico.html', correo=email_m, nombre=nombre)
    return redirect(url_for('inicio_medico'))   

@app.route('/login.html', methods=['GET','POST'])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password = request.form.get("password")
        if correo and password:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM pacientes WHERE correo=%s AND password=%s', (correo,password))
            record = cur.fetchone()
            if record:
                session['loggedin'] = True
                session['correo'] = correo
                session['nombre'] = record[0] 
                return redirect(url_for("dashboard"))
            else:
                flash("Correo o Password Invalidos!")
        else:
            flash("Correo o Password Invalidos!")
    return redirect(url_for("inicio"))

@app.route('/registro.html')
def registro():
    return render_template("registro.html")

@app.route('/inicio_medico.html')
def inicio_medico():
    return render_template("inicio_medico.html")

@app.route('/registro_medico.html')
def registro_medico():
    return render_template("registro_medico.html")
    
