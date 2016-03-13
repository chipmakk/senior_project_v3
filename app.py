#python imports 
from flask import Flask, render_template, redirect, url_for, request, flash
import os
import os.path
from train import trainprog 
import subprocess 
import sys
import glob
import select
import cv2
import base64
import time
from PIL import Image 
import config
import face
#define the application
app = Flask(__name__)

#App Home page 
@app.route ('/')
def home():
	return render_template("index.html")
#=========================================================================================
#Admin login page w/ form 
@app.route("/adminlogin", methods =['GET','POST'])
def adminlogin():
	error = None
	if request.method == 'POST':
		#if uname and pw does not equal specified value then error is prompted 
		if request.form['username'] !='admin' or request.form ['password'] !='admin':
			error = 'Invalid Credentials. Try again'
		#if uname and pw does equal specified value then redirect to Admin option page
		else: 
			return redirect(url_for('admin'))
	#renders adminlogin forms
	return render_template('adminlogin.html', error=error)

#admin option page with 3 functions 
@app.route("/admin", methods = ['GET','POST'])
def admin():
	return render_template('adminopt.html')

#=========================================================================================
#user Home login page linked to capture profile page 
@app.route("/user", methods =['GET','POST']) 
def add():
	return render_template('facelogin.html')
	
#=========================================================================================
#Admin --> new user page with 3 functions one for linux acct - image repo-- premissions
@app.route("/new", methods =['GET','POST'])
def new():
	return render_template('addusers.html')
	
#Form for adding a new linux user html
@app.route("/linuxuser")
def my_form():
	return render_template('linuxuser.html')
#Iniates the addlinuxuser.sh script and passes values from form 
@app.route('/linuxuser', methods=['POST'])
def my_form_post():
	username = request.form['uname']
	x = username
	passwd = request.form['pass']
	return str(subprocess.check_call(["./shell/addlinuxuser.sh", x,passwd], shell=False)) and redirect(url_for('new'))
#==================================================================================================
 #Remove linux user html
@app.route('/removelinuxuser', methods=['GET'])
def remove_form():
	return render_template('remove.html')

#Iniates the removelinux.sh script and passes values from the form  
@app.route('/removelinuxuser', methods=['POST'])
def remove_form_post():
	username = request.form['uname']
	x = username
	passwd = request.form['pass']
	return str(subprocess.check_call(["./shell/removelinuxuser.sh", x,passwd], shell=False)) and redirect(url_for('admin'))
#==========================================================================================

#Admin add new user function to positive image repo
@app.route ('/pos', methods=['GET'])
def pos():
	return render_template("capture.html")



@app.route("/capture", methods =['POST'])
def admincapture():	
	
	data = request.form['mydata']
	#print data 
	#need to decode data here
	#open image path to save after decode
	img = open("userimg/capture.jpg", "wb")
	img.write(data.decode('base64'))
	img.close()
	#open image and convert to pgm format
	im = Image.open('userimg/capture.jpg')
	im = im.convert('RGB')
	im.save('userimg/capture.pgm')

	# Prefix for positive training image files
	POSITIVE_FILE_PREFIX = 'positive_'
	# Create the directory for positive training images if it doesn't exist.
	if not os.path.exists(config.POSITIVE_DIR):
			os.makedirs(config.POSITIVE_DIR)
	# Find the largest ID of existing positive images.
	# Start new images after this ID value.
	files = sorted(glob.glob(os.path.join(config.POSITIVE_DIR, 
		POSITIVE_FILE_PREFIX + '[0-9][0-9][0-9].pgm')))
	count = 0
	if len(files) > 0:
		# Grab the count from the last filename.
		count = int(files[-1][-7:-4])+1

	while True:
		xx= cv2.imread('userimg/capture.pgm')
		print type(xx)
		yy = cv2.cvtColor(xx,cv2.COLOR_RGB2GRAY)
		cv2.imwrite('userimg/capture2.pgm',yy) 

		image = cv2.imread('userimg/capture2.pgm')
		result = face.detect_single(image)
		if result is None:
			print 'not detected'
			flash("User Profile Not Detected",'danger')
			#return 'not detected'
			return render_template("capture.html")
		break
	x, y, w, h = result
	crop = face.crop(image, x, y, w, h)
	filename = os.path.join(config.POSITIVE_DIR, POSITIVE_FILE_PREFIX + '%03d.pgm' % count)
	cv2.imwrite(filename,crop)
	if True:
		print 'Captured sucess!'
		flash("Profile Captured Sucessfuly", 'success')
		time.sleep(3)
		#return 'capture sucess'
		return render_template("capture.html")




#===========================================================================================================
#permissions
@app.route('/permissions')
def permissions():
	return render_template('permissions.html')

@app.route('/permissions',methods=['POST','GET'])
def permissions_post():
	username = request.form['username']
	if request.form["submit"] == 'levela':
		return str(subprocess.check_call(["./shell/levela.sh", username], shell=False)) and redirect(url_for('permissions'))
	elif request.form["submit"] == 'levelb':
		return str(subprocess.check_call(["./shell/levelb.sh", username], shell=False)) and redirect(url_for('permissions'))
	elif request.form["submit"] == 'levelc':
		return str(subprocess.check_call(["./shell/levelc.sh", username], shell=False))	and redirect(url_for('permissions'))
#=======================================================================================

#Runs the Train Data program -->sends admin to admin logout screen --> need to pass error message from train data prog..
@app.route("/trainprog", methods = ['GET',"POST"])
def train():
	if request.method == 'GET':
		trainprog()
		return render_template('train.html')

#User login/ recog function face regonization 
@app.route ('/comp', methods=['POST'])
def comp():
	datab = request.form['comp']
	#print datab 
	#open image path to save after decode
	inital = open("limage/attempt.jpg", "wb")
	inital.write(datab.decode('base64'))
	inital.close()
	#open image and convert to pgm format
	second = Image.open('limage/attempt.jpg')
	second = second.convert('RGB')
	second.save('limage/attempt.pgm')

	print 'Loading training data...'
	#initalize opencv facerecognizer class
	model = cv2.createEigenFaceRecognizer()
	#loads xml training file creaded by train.py
	model.load(config.TRAINING_FILE)
	print 'Training data loaded!'
	print 'Capturing Profile...'
	#start loop to process users image 
	while True:
		#read in converted pgm image and change to grayscale
		third= cv2.imread('limage/attempt.pgm')
		#print type(third)
		compare = cv2.cvtColor(third,cv2.COLOR_RGB2GRAY)
		#run face detect cv process
		result = face.detect_single(compare)
		if result is None:
				print 'Could not detect one face!'
				#return "User Not Detected"
				flash("User Not Detected! Please retake image", 'danger')
				return render_template('facelogin.html')
				break
		x, y, w, h = result
		# Crop and resize image to face.
		crop = face.resize(face.crop(compare, x, y, w, h))
		#write debug image after crop and resize peformed 
		cv2.imwrite('limage/debug.pgm',crop)
	
		#read croped image for model to process--prevents wrong shape matrices error 
		final = cv2.imread('limage/debug.pgm',0)
		# Test user face against model
		label, confidence = model.predict(final)
		print 'Predicted face with confidence {1} (lower is more confident).'.format(
					'POSITIVE' if label == config.POSITIVE_LABEL else 'NEGATIVE', 
					confidence)
		#if confidence level is less than set threshold in config.py user is accepted
		if label == config.POSITIVE_LABEL and confidence < config.POSITIVE_THRESHOLD:
			#return 'Accepted User'
			flash("User Accepted", 'success')
			return render_template('facelogin.html')
		#user is denied if confidence level is greater than set threshold in config.py	
		else:
			print 'Did not recognize user!'
			#return 'User Not Accepted !'
			flash("User Not Accepted!", 'danger')
			return render_template('facelogin.html')

#User login page after face recgonize 
#@app.route('/user_login', methods=['GET','POST'])
#def user_login():
	#return str(subprocess.check_call(["./shell/userlogin.sh"], shell=False))

#end of app
  #end of app
if __name__ == "__main__":
	app.secret_key = 'test'
	app.debug = True
	app.run(host='0.0.0.0')

