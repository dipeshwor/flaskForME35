# SNAPR - Snap, Narrate, Auto Post and Reflect
# December 19, 2019 
# Tufts University 
# Tufts Center for Engineering Education and Outreach

# Keywords
# Canvas, Flask
# Hardware - Raspberry Pi Zero W, RPi Camera

# Code for Video streaming modified from 
# https://github.com/miguelgrinberg/flask-video-streaming

# Import necessary libraries   
from flask import Flask, render_template, request, Response, send_file
app = Flask(__name__)
from datetime import datetime
import time, io, threading
import requests, os, picamera

# Set up a session
session = requests.Session()

# Define variables
message1 = 'Dipeshwor M. Shrestha'
message2 = '1'
message3 = 'dipeshwor-m-shrestha'
message4 = ''

# Folder where the code resides 
rootFolder='/home/pi/Desktop/SNAPR/'
filename=rootFolder+'files/documentationSetup.PNG'

# Set flags 
flag=0
stopFlag=0
delay=1

# Part 2: Flask

# Video streaming 
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask 
def gen(camera):
	"""Video streaming generator function."""
	global flag
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
			b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

class Camera(object):
	thread = None  # background thread that reads frames from camera
	frame = None  # current frame is stored here by background thread
	last_access = 0  # time of last client access to the camera

	def initialize(self):
		if Camera.thread is None:
			# start background frame thread
			Camera.thread = threading.Thread(target=self._thread)
			Camera.thread.start()
			# wait until frames start to be available
			while self.frame is None:
				time.sleep(0)

	def get_frame(self):
		Camera.last_access = time.time()
		self.initialize()
		return self.frame

	@classmethod
	def _thread(cls):
		while True:
			global flag, delay, message1, stopFlag, filename
			with picamera.PiCamera() as camera:
				# camera setup
				#camera.resolution = (1080, 720)
				camera.resolution = (640, 480)
				#camera.resolution = (320, 240)
				#camera.hflip = True
				#camera.vflip = True
				#camera.rotation=270

				stream = io.BytesIO()
				for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
					# store frame
					stream.seek(0)
					cls.frame = stream.read()

					# reset stream for next frame
					stream.seek(0)
					stream.truncate()
					#When flag is raised start capturing and uploading files to Canvas 
					#if flag==1:
					#for filename in camera.capture_continuous(rootFolder+'files/img{timestamp:%Y%m%d_%H%M%S}.jpg'):
					#for filename in camera.capture_continuous(rootFolder+'files/image.jpg'):
					filename=rootFolder+'files/image.jpg'	
					camera.capture(filename)
					#print('Captured %s' % filename)
					#time.sleep(0.1)
						
					# if there hasn't been any clients asking for frames in
					# the last 120 seconds stop the thread
					if time.time() - cls.last_access > 120:
						break

			cls.thread = None

#Index page 
@app.route('/index', methods = ['POST', 'GET'])
def index():
	global message1, message2, message3, message4, flag, filename
	message1="In Progress"	

	templateData = {
		'msg1'  : message1,
		'msg2'  : message2, 
		'msg3': message3,
		'msg4': message4,
		'flag': flag
	}
	return render_template('index.html', **templateData)

#Download page
#Has the latest captured image 
#You can use a GET from another app to get the latest captured image 
@app.route('/download')
def download():
	global filename
	try:
		return send_file(filename, attachment_filename='image.jpg')
	except Exception as e:
		return str(e)

#Video feed path 
@app.route('/video_feed')
def video_feed():
	"""Video streaming route. Put this in the src attribute of an img tag."""
	return Response(gen(Camera()),
		mimetype='multipart/x-mixed-replace; boundary=frame')

# Flash server on port 80
# Open up a browser and enter the RPi IP 
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True, threaded=True)