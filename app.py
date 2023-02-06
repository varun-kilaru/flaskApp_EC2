from flask import Flask, render_template, url_for, redirect, session, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.app_context().push()

print('File name : ', os.path.basename(__file__))
print('Directory Name:   ', os.path.dirname(__file__))
absolute_path = os.path.dirname(__file__)
db_path = 'sqlite:///'+ absolute_path +'/database.db' 
files_path = os.path.join(absolute_path, 'tmp')
print(files_path)


bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['UPLOAD_FOLDER'] = files_path
app.config['SECRET_KEY'] = '164338448224012766796679500138822656752'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    firstname = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Firstname"})

    lastname = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Lastname"})

    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})


    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

def count_words(file):
    number_of_words = 0
    print(os.path.join(files_path,file))
    filepath = os.path.join(files_path,file)
    with open(filepath,'r',errors='ignore') as file:
        data = file.read()
        lines = data.split()
        number_of_words += len(lines)
    return number_of_words


@app.route('/countwords', methods=['GET', 'POST'])
@login_required
def countwords():
    user = session['user']
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # print(type(uploaded_file))
            # print(uploaded_file.stream)
            # uploaded_file.save(secure_filename(uploaded_file.filename))
            dddd = os.path.join(files_path, uploaded_file.filename)
            p = uploaded_file.filename
            uploaded_file.save(dddd)
            num_words = count_words(uploaded_file.filename)
            print(dddd)
    # return redirect(url_for('countwords'), user=user)
            return render_template('countwords.html', user=user, words=num_words, path=p)
    else:
        return render_template('countwords.html', user=user)

@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/sign-in', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                # print(user.username)
                session['user'] = user.username
                return redirect(url_for('countwords'))
        else:
            return render_template('login.html', form=form, message="register first!")
    return render_template('login.html', form=form)


# @app.route('/countwords', methods=['GET', 'POST'])
# @login_required
# def countwords():
#     user = session['user']
#     return render_template('countwords.html', user=user)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/download/<filename>', methods=['GET', 'POST'])
@login_required
def download(filename):
    print(filename)
    path = files_path 
    return send_from_directory(path, filename, as_attachment=True)


@ app.route('/register', methods=['GET', 'POST'])
@app.route('/sign-up', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)