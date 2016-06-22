#!/usr/bin/env python
from time import sleep
from gpiozero import Button
import os, random, picamera
from neopixel import *
from subprocess import Popen

### !! VAR DEFINITIONS !! ###


# LED strip configuration. #1 is at button, #2 at the camera
LED_COUNT1     	= 24      # Number of LED pixels.
LED_COUNT2     	= 16      # Number of LED pixels.
LED_PIN       	= 18      # GPIO pin connected to the button pixels (must support PWM!).
LED_FREQ_HZ    	= 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        	= 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS	= 50      # Set to 0 for darkest and 255 for brightest
LED_BRIGHTFAC 	= 0.2     # factor of the default brightness
LED_INVERT     	= False   # True to invert the signal (when using NPN transistor)

# GPIO pins according to BCM (http://pinout.xyz)
PINBTN = 23



# Picture configuration
PICTURE_COUNT   = 5
RESOLUTION 		= (1280, 720)



# Picture wait delays
COMPLIMENT_WAIT = 0.8 # seconds
REPLAY_WAIT     = 12 # seconds
GOODBYE_WAIT    = 6 # seconds
STARTING_WAIT	= 2500/LED_COUNT1	# if we wait that amount after each LED, the whole process takes 1 second
PHOTOSHOOT_WAIT	= 500/LED_COUNT2	# time between photos
GIF_DELAY = 25 # How much time (1/100th seconds) between frames in the animated gif



# Color values (CAUTION: NOT RGB but GRB: Green, Red, Blue)
COLOR_OK = Color(255, 0, 0)	#GREEN
COLOR_BLACK = Color(0, 0, 0) # BLACK
COLOR_INITCOUNTDOWN1 = Color(150, 0, 0)
COLOR_INITCOUNTDOWN2 = Color(30, 0, 0)
COLOR_INITCOUNTDOWN3 = Color(10, 0, 0)
COLOR_INITCOUNTDOWN4 = Color(5, 0, 0)
COLOR_IMAGECOUNTDOWN = Color(35, 15, 105)
COLOR_GIFGENERATION = Color(0, 0, 255)
COLOR_GIFGENERATIONDARK = Color(0, 0, 120)
COLOR_REPLAY = Color(255, 255, 255)



# Paths
PATH_FILEPATH = '/home/pi/photobooth/'
PATH_OUTPUT = PATH_FILEPATH + 'output/'
PATH_OUTPUTROUND = PATH_OUTPUT + 'round%06d/'
PATH_OUTPUTFILE = PATH_OUTPUTROUND + 'frame%02d.jpg'
PATH_OUTPUTFILEGIF = PATH_OUTPUT + 'round%06d.gif'

# Branding logo overlay
OVERLAYIMAGE_SRC = PATH_FILEPATH + 'media/logo.png'
OVERLAYIMAGE_OFFSET = (50, 30)



# Camera text annotations
CAMERA_TEXTCOLOR = picamera.Color('white')
CAMERA_TEXTBACKGROUNDCOLOR = picamera.Color('black')

CAMERA_TEXTVAL_START = 'Get %d poses ready & press the button to start'%PICTURE_COUNT
CAMERA_TEXTVAL_STARTING1 = 'Photobooth is starting'
CAMERA_TEXTVAL_STARTING2 = 'It will take %d pictures'%PICTURE_COUNT
CAMERA_TEXTVAL_STARTING3 = 'The camera LED circle will fill up'
CAMERA_TEXTVAL_STARTING4 = 'When it\'s full, a photo is taken'
CAMERA_TEXTVAL_STARTING5 = 'Get ready! We are launching.'
CAMERA_TEXTVAL_PICINFORMATION = 'Taking picture #%d'
CAMERA_TEXTVAL_PROCESSING = 'Stitching your photos together. Please wait a few seconds.'
CAMERA_TEXTVAL_PROCESSINGDONE = 'Almost there'
CAMERA_TEXTVAL_GOODBYE = 'It was great having you here! See you around.'

# List of compliments displayed after each photo. Needs atleast as many entries as the picture count!!!
CAMERA_TEXTVAL_COMPLIMENTS = ['Looking good!', 'Oh yeah!', 'You rock!', 'Just like that!', 'Keep it up!', 'Yes!', 'Great!', 'Oh wow!', 'Perfect!', 'Nice!']

### !! DEFINITIONS DONE !! ###



### !! NEO PIXEL ANIMATIONS - SEE https://github.com/jgarff/rpi_ws281x !! ###

# Create NeoPixel object with appropriate configuration and intialize the library
strip = Adafruit_NeoPixel(LED_COUNT1+LED_COUNT2, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()



# Define functions which animate LEDs in various ways.
# Asuming the default call is for the button LEDs
def colorWipe(strip, color, wait_ms=20, isButtonLEDs=True):
	add = LED_COUNT1 if isButtonLEDs else 0	# offset the leds for the camera leds
	count = LED_COUNT2 if isButtonLEDs else LED_COUNT1	# offset the leds for the camera leds

	# wipe color: do a radiant animation with this color
	for i in range(count):
		strip.setPixelColor(i+add, color)
		strip.show()
		if wait_ms > 0:
			sleep(wait_ms/1000.0)

# Show color instantaneous w/o any animation
def colorClear(strip, color, isButtonLEDs=True):
	colorWipe(strip, color, wait_ms=0, isButtonLEDs=isButtonLEDs)


### !! NEO PIXEL ANIMATIONS DONE !! ###


### !! CAMERA FUNCTIONS !! ###

def cameraDisplayText(camera, text):
	if text:
		camera.annotate_background = CAMERA_TEXTBACKGROUNDCOLOR
		camera.annotate_text = ' '+text+' '
	else:
		camera.annotate_background = None
		camera.annotate_text = ''


### !! BUSINESS LOGIC START !! ###

# start the camera
camera = picamera.PiCamera()
camera.resolution = RESOLUTION

# turn off that red camera led
camera.led = False

# set camera annotation text color
camera.annotate_foreground = CAMERA_TEXTCOLOR

# start the camera preview and show the ok color w/ animation
camera.start_preview()
colorWipe(strip, COLOR_OK)
colorClear(strip, COLOR_BLACK, isButtonLEDs=False)
cameraDisplayText(camera, CAMERA_TEXTVAL_START)

# get the hardware button
button = Button(PINBTN)

# round increment
mround = 0

while True:

	# try to create a folder (don't abort if already there)
	try:
		os.mkdir(PATH_OUTPUTROUND%mround, 0777)
	except OSError:
		print "dir already there"

	# wait for the button press
	button.wait_for_press()
	cameraDisplayText(camera, CAMERA_TEXTVAL_STARTING1)

	# do start animation
	colorWipe(strip, COLOR_INITCOUNTDOWN1, wait_ms=STARTING_WAIT)
	cameraDisplayText(camera, CAMERA_TEXTVAL_STARTING2)
	colorWipe(strip, COLOR_INITCOUNTDOWN2, wait_ms=STARTING_WAIT)
	cameraDisplayText(camera, CAMERA_TEXTVAL_STARTING3)
	colorWipe(strip, COLOR_INITCOUNTDOWN3, wait_ms=STARTING_WAIT)
	cameraDisplayText(camera, CAMERA_TEXTVAL_STARTING4)
	colorWipe(strip, COLOR_INITCOUNTDOWN4, wait_ms=STARTING_WAIT)
	cameraDisplayText(camera, CAMERA_TEXTVAL_STARTING5)
	colorWipe(strip, COLOR_BLACK, wait_ms=STARTING_WAIT)

	# get x random unique compliments
	compliment_shuffle = random.sample(CAMERA_TEXTVAL_COMPLIMENTS, PICTURE_COUNT)

	# frame animate
	frame = 0

	# loop through the pictures
	while frame < PICTURE_COUNT:
		# show photo number and start light animation
		cameraDisplayText(camera, CAMERA_TEXTVAL_PICINFORMATION%(frame+1))
		colorWipe(strip, COLOR_IMAGECOUNTDOWN, wait_ms=PHOTOSHOOT_WAIT, isButtonLEDs=False)

		# clear the text and take a picture
		cameraDisplayText(camera, False)
		filepath = PATH_OUTPUTFILE%(mround,frame)
		camera.capture(filepath, use_video_port=True)

		# add branding and scale down the image using graphicsmagick
		graphicsmagick  = "gm composite "
		graphicsmagick += "-gravity SouthEast -geometry +" + str(OVERLAYIMAGE_OFFSET[0]) + "+" + str(OVERLAYIMAGE_OFFSET[0]) + " "	# bottom right with padding
		graphicsmagick += OVERLAYIMAGE_SRC + " " + filepath + " " + filepath # overlay image, source image, target image
		print graphicsmagick
		os.system(graphicsmagick)

		# clear the lights
		colorClear(strip, COLOR_BLACK, isButtonLEDs=False)

		# show a compliment and sleep for a bit
		cameraDisplayText(camera, compliment_shuffle[frame])
		sleep(COMPLIMENT_WAIT)

		frame += 1

	# show git generation lights
	cameraDisplayText(camera, CAMERA_TEXTVAL_PROCESSING)
	colorWipe(strip, COLOR_GIFGENERATION)
	colorWipe(strip, COLOR_GIFGENERATIONDARK, isButtonLEDs=False)

	# create the gif
	graphicsmagick = "gm convert -delay " + str(GIF_DELAY) + " " + PATH_OUTPUTROUND%mround + "*.jpg " + PATH_OUTPUTFILEGIF%mround 
	os.system(graphicsmagick) #make the .gif

	# start the gif viewer
	command = ["viewnior", "--fullscreen", PATH_OUTPUTFILEGIF%mround]
	p = Popen(command)

	# display the text telling it is almost done, since we still need time to start the replay
	cameraDisplayText(camera, CAMERA_TEXTVAL_PROCESSINGDONE)

	# starting the gif viewer takes some time, so dont close the preview right away
	sleep(2)
	colorWipe(strip, COLOR_BLACK, isButtonLEDs=False)
	camera.stop_preview()
	colorWipe(strip, COLOR_REPLAY)

	# wait x seconds while showing the replay
	sleep(REPLAY_WAIT)

	# start the camera preview and close the gif viewer
	camera.start_preview()
	p.terminate()
	p.wait()

	# display the goodbye text
	cameraDisplayText(camera, CAMERA_TEXTVAL_GOODBYE)
	sleep(GOODBYE_WAIT)

	# show the ok color w/ animation
	colorWipe(strip, COLOR_OK)
	cameraDisplayText(camera, CAMERA_TEXTVAL_START)

	mround += 1

### !! BUSINESS LOGIC DONE !! ###