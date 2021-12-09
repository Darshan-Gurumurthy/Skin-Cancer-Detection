from __future__ import division, print_function
import sys
import os
import glob
import re
from pathlib import Path
from io import BytesIO
import base64
import requests
import datetime

#password hashing
from werkzeug.security import generate_password_hash, check_password_hash


# for generating pdf
import pdfkit

# Import fast.ai Library
from fastai import *
from fastai.vision import *

from werkzeug.utils import secure_filename
# Flask utils
from flask import Flask, redirect, url_for, render_template, request, session, flash
from PIL import Image as PILImage

# DB_connection
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])
# Define a flask app
app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['PDF_FOLDER'] = 'static/uploads/'
app.config['TEMPLATE_FOLDER'] = 'templates/'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'SCD'

mysql = MySQL(app)


NAME_OF_FILE = 'model' # Name of your exported file
PATH_TO_MODELS_DIR = Path('.') # by default just use /models in root dir
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis',
           'Dermatofibroma', 'Melanocytic nevi', 'Melanoma', 'Vascular lesions']

def setup_model_pth(path_to_pth_file, learner_name_to_load, classes):
    data = ImageDataBunch.single_from_classes(
        path_to_pth_file, classes, ds_tfms=get_transforms(), size=224).normalize(imagenet_stats)
    learn = cnn_learner(data, models.densenet169, model_dir='models')
    learn.load(learner_name_to_load, device=torch.device('cpu'))
    return learn

learn = setup_model_pth(PATH_TO_MODELS_DIR, NAME_OF_FILE, classes)

def encode(img):
    img = (image2np(img.data) * 255).astype('uint8')
    pil_img = PILImage.fromarray(img)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

def model_predict(img):
    img = open_image(BytesIO(img))
    pred_class,pred_idx,outputs = learn.predict(img)
    formatted_outputs = ["{:.1f}%".format(value) for value in [x * 100 for x in torch.nn.functional.softmax(outputs, dim=0)]]
    pred_probs = sorted(
            zip(learn.data.classes, map(str, formatted_outputs)),
            key=lambda p: p[1],
            reverse=True
        )

    img_data = encode(img)
    result = {"class":pred_class, "probs":pred_probs, "image":img_data}
    return render_template('result.html', result=result)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        usr = cursor.execute('SELECT password FROM accounts WHERE username = % s', (username, ))
        print (usr)
        if not usr:
            flash("Incorrect username / password !","info")
            return render_template('login.html', msg = msg)
        temp_pass = cursor.fetchone()
        print (temp_pass['password'])
        print (password)
        result_pass = check_password_hash(temp_pass['password'], password)
        print (result_pass)
        #result_pass=False
        if (result_pass):
            cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
            account = cursor.fetchone()
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            flash("Logged in successfully !","info")
            return render_template('scd.html', msg = msg)

        else:
            flash("Incorrect username / password !","info")
            return render_template('login.html', msg = msg)
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    if session['loggedin'] == True:
        user = session['username']
        flash(f"You have been logged out,{user}", "info")
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    print ("in changePassword")
    msg = ''
    if request.method == 'POST' and 'OldPassword' in request.form and 'NewPassword' in request.form and 'ConfirmPassword' in request.form :
        OldPassword = request.form['OldPassword']
        NewPassword = request.form['NewPassword']
        ConfirmPassword = request.form['ConfirmPassword']
        username = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT password FROM accounts WHERE username = % s', (username, ))
        temp_pass = cursor.fetchone()
        result_pass = check_password_hash(temp_pass['password'], OldPassword)
        print (result_pass)
        if not (result_pass):
            flash("Old Password Does not match","info")
            return render_template('changePassword.html', msg = msg)
        elif not (ConfirmPassword == NewPassword):
            flash("Confirm Password does not match New Password","info")
            return render_template('changePassword.html', msg = msg)
        else:
            password = generate_password_hash(ConfirmPassword, method='sha256')
            cursor.execute('UPDATE accounts SET password = % s  WHERE username = % s;', (password, username, ))
            mysql.connection.commit()
            flash("You have successfully Changed Password !","info")
            flash("","info")
            return render_template('changePassword.html', msg = msg)
    return render_template('changePassword.html', msg = msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        password = generate_password_hash(password, method='sha256')
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            flash("Account already exists !","info")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address !","info")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers !","info")
        elif not username or not password or not email:
            flash("Please fill out the form !","info")
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            flash("You have successfully registered !","info")
    elif request.method == 'POST':
        flash("Please fill out the form!!","info")
    return render_template('register.html', msg = msg)

@app.route('/scd', methods=['GET', "POST"])
def scd():
    # Main page
    return render_template('scd.html')


@app.route('/upload', methods=["POST", "GET"])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        img = request.files['file'].read()

        if img != None:
            file = request.files['file']
            a = app.config['UPLOAD_FOLDER']
            file.save(os.path.join(a , file.filename))

        # Make prediction
            preds = model_predict(img)
            with open("templates/temp.html", "w") as file1:
                #to convert html into pdf
                # Writing data to a file
                #file1.write("Hello \n")
                file1.writelines(preds)

            return preds
    return 'OK'





if __name__ == '__main__':
    port = os.environ.get('PORT', 8008)

    if "prepare" not in sys.argv:
        app.run(debug=False, host='0.0.0.0', port=port)
