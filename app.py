import bcrypt
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, URL
from flask_mysqldb import MySQL

app = Flask(__name__)

# MYSQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'opticool_test'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    # validate email
    def validate_email(self,field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where email=%s",(field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class EyeglassesForm(FlaskForm):
    # link = StringField("Link Website", validators=[URL()])
    name = StringField("Name", validators=[DataRequired()])
    brand = StringField("Brand", validators=[DataRequired()])
    # faceShape = StringField("Face Shape")
    price = StringField("Price", validators=[DataRequired()])
    gender = StringField("Gender", validators=[DataRequired()])
    # frameColour = StringField("Frame Color")
    # frameShape = StringField("Frame Shape")
    # frameStyle = StringField("Frame Style")
    # linkPic1 = StringField("Link Pic 1")
    # linkPic2 = StringField("Link Pic 2")
    # linkPic3 = StringField("Link Pic 3")
    # frameMaterial = StringField("Frame Material")
    submit = SubmitField("Submit")

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM eyeglasses")
        data = cursor.fetchall()
        cursor.close()
        return render_template('dashboard.html', data = data)

    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html',form=form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        #store db
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form = form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logout Sukses")
    return redirect(url_for('login'))

@app.route('/create', methods = ['GET', 'POST'])
def create_eyeglasses():
    if 'user_id' in session:
        form = EyeglassesForm()
        if form.validate_on_submit():
            name = form.name.data
            brand = form.brand.data
            price = form.price.data
            gender = form.gender.data

            #store db
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO eyeglasses (name, brand, price, gender) VALUES (%s, %s, %s, %s)", (name, brand, price, gender))
            mysql.connection.commit()
            cursor.close()

            flash("Eyeglasses successfully added")
            return redirect(url_for('dashboard'))

        return render_template('create.html', form = form)

    return redirect(url_for('login'))

@app.route('/<id>/update', methods = ['GET', 'POST'])
def update_eyeglasses(id):
    if 'user_id' in session:
        form = EyeglassesForm()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM eyeglasses WHERE id = %s", (id,))
        data = cursor.fetchone()
        cursor.close()

        if form.validate_on_submit():
            name = form.name.data
            brand = form.brand.data
            price = form.price.data
            gender = form.gender.data

            #store db
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE eyeglasses SET name = %s, brand = %s, price = %s, gender = %s WHERE id = %s", (name, brand, price, gender, id))
            mysql.connection.commit()
            cursor.close()

            flash("Eyeglasses successfully edited")
            return redirect(url_for('dashboard'))

        return render_template('update.html', form = form, data = data)
    
    return redirect(url_for('login'))

@app.route('/<id>/delete', methods=['GET'])
def delete(id):
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM eyeglasses WHERE id = %s", (id,))
        mysql.connection.commit()
        flash("Eyeglasses successfully deleted")

        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('profile.html', user = user)
        
    return redirect(url_for('login'))

@app.route('/products')
def products():
    return render_template('products.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)