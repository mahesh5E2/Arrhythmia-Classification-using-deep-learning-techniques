from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
import sqlite3

# Define a flask app
app = Flask(__name__)


@app.route('/')
def home():
	return render_template('home.html')

@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')

@app.route("/signup")
def signup():

    username = request.args.get('user','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
    con.commit()
    con.close()
    return render_template("signin.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == 'admin' and password1 == 'admin':
        return render_template("index.html")

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("index.html")
    else:
        return render_template("signup.html")
        
@app.route('/index', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')



model_path2 = 'model/model-dense.h5' # load .h5 Model
classes2 = {0:"Fusion of ventricular and normal beat",1:"Missed Beat",2:"Normal",3:"Unclassifiable beat",4:"Supraventricular premature beat",5:"Premature ventricular contraction"}
CTS = load_model(model_path2)
from keras.preprocessing.image import load_img, img_to_array
def model_predict2(image_path,model):
    print("Predicted")
    image = load_img(image_path,target_size=(224,224))
    image = img_to_array(image)
    image = image/255
    image = np.expand_dims(image,axis=0)
    
    result = np.argmax(model.predict(image))
    prediction = classes2[result]  
    
    if result == 0:
        return "Fusion of ventricular and normal beat", "result.html"        
    elif result == 1:
        return "Missed Beat","result.html"
    elif result == 2:
        return "NORMAL BEAT","result.html"
    elif result == 3:
        return "Unclassifiable beat","result.html"
    elif result == 4:
        return "Supraventricular premature beat","result.html"
    elif result == 5:
        return "Premature ventricular contraction","result.html"
    


@app.route('/predict2',methods=['GET','POST'])
def predict2():
    print("Entered")
    if request.method == 'POST':
        print("Entered here")
        file = request.files['file'] # fet input
        filename = file.filename        
        print("@@ Input posted = ", filename)
        
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = model_predict2(file_path,CTS)
              
        return render_template(output_page, pred_output = pred)


    #this section is used by gunicorn to serve the app on Heroku
if __name__ == '__main__':
        app.run(debug=False)
   