import os
import re
import MySQLdb
from flask import Flask, render_template, request, flash, url_for, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'realEstate'
mysql = MySQL(app)

with app.app_context():
    cursor = mysql.connection.cursor()
    cursor.execute('''create table if not exists users (user_id int primary key AUTO_INCREMENT,nom varchar(50),
     prenom varchar(50),adresse varchar(100),email varchar(100), role int,date_naissance Date , num_tel varchar(100), password varchar(100));''')
    cursor.execute('''create table if not exists region (region_id int primary key AUTO_INCREMENT, nom_region varchar(50)
         );''')
    cursor.execute('''create table if not exists immobilier (immobilier_id int primary key AUTO_INCREMENT,prix int,
      nb_chambre int , id_region int , user_id int ,date_ajout Date , description text, foreign key (id_region) references region(region_id),
        foreign key (user_id) references users (user_id) , disponibilite int );''')
    cursor.execute('''create table if not exists avis (avis_id int primary key AUTO_INCREMENT, avis varchar(50),
        user_id int,immobilier_id int , foreign key (user_id) references users (user_id), foreign key (immobilier_id) references immobilier (immobilier_id) );''')
    cursor.close()


@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('home.html', nom=session['nom'], prenom=session['prenom'])
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['post', 'get'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))

        # Fetch one record and return result
        user = cursor.fetchone()

        # If account exists in accounts table in out database
        if user:

            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user['user_id']
            session['nom'] = user['nom']
            session['prenom'] = user['prenom']

            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'nom' in request.form and 'prenom' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        nom = request.form['nom']
        prenom = request.form['prenom']
        password = request.form['password']
        email = request.form['email']
        num_tel = request.form['num_tel']
        adresse = request.form['adresse']
        date_naissance = request.form['date_naissance']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE nom = %s', (nom,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', nom):
            msg = 'nom must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', prenom):
            msg = 'nom must contain only characters and numbers!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users (nom,prenom,adresse,email,role,date_naissance,num_tel,password)'
                           ' VALUES (%s, %s, %s, %s, 0, %s, %s, %s)',
                           [nom, prenom, adresse, email, date_naissance, num_tel, password])
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form2!'
        # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/logout')
def logout():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)
