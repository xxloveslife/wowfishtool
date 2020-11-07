import logging
import cv2
import pyscreenshot as ImageGrab
import numpy as np
import autopy
from matplotlib import pyplot as plt

import pyaudio
import wave
import audioop
from collections import deque
import os
import time
import math
import psutil

dev = False

screen_size = None
screen_start_point = None
screen_end_point = None



def check_process():
	print('Checking WoW is running')
	# print 'Checking WoW is running'
	# wow_process_names = ["World of Warcraft"]
	wow_process_names = ["Wow.exe"]
	running = False
	for pid in psutil.pids():
		p = psutil.Process(pid)
		# print(p)
		if any(p.name() in s for s in wow_process_names):
			print(p.name())
			running = True
	if not running and not dev:
		print(running,dev)
		print('WoW is not running')
		# print 'WoW is not running'
		exit()
	print('WoW is running')
	return running
	# print 'WoW is running'
		# raw_input('Pleas e put your fishing-rod on key 1, zoom-in to max, move camera on fishing-float and press any key')



def check_screen_size():
	print("Checking screen size")
	# print "Checking screen size"
	img = ImageGrab.grab()
	# print('img.size',img.size)
	# img.save('temp.png')
	global screen_size
	global screen_start_point
	global screen_end_point

	screen_size = (img.size[0] / 2, img.size[1] / 2)     #(960,540)  #全屏幕除以2

	screen_start_point = (screen_size[0] * 0.35, screen_size[1] * 0.35)   #(336,189)
	# print("start_point",screen_start_point)
	screen_end_point = (screen_size[0] * 0.65, screen_size[1] * 0.65)   #(624,351)
	# print("end_point",screen_end_point)
	# print('startAndEnd',screen_start_point,screen_end_point)
	print ("Screen size is " + str(screen_size))


def send_float():
	print('Sending float')
	# print 'Sending float'
	autopy.key.tap(autopy.key.Code.F1)
	# autopy.key.tap("w", [autopy.key.Modifier.META])
	print('Float is sent, waiting animation')
	# print 'Float is sent, waiting animation'
	time.sleep(2)

def jump():
	print('Jump')
	# print 'Jump!'
	# autopy.key.tap(u' ')
	time.sleep(1)

def make_screenshot():
	print( 'Capturing screen')
	# print 'Capturing screen'
	# print(screen_start_point)
	# screenshot = ImageGrab.grab((screen_start_point[0], screen_start_point[1], screen_end_point[0], screen_end_point[1])) # (0, 710, 410, 1010)
	screenshot = ImageGrab.grab((300,100,1400,600))
	# print(screenshot.size)
	if dev:
		screenshot_name = 'var/fishing_session_' + str(int(time.time())) + '.png'
	else:
		screenshot_name = 'var/fishing_session.png'
	screenshot.save(screenshot_name)
	return screenshot_name

def find_float(img_name):
	print('Looking for float')
	# print 'Looking for float'
	# todo: maybe make some universal float without background?
	for x in range(0, 1):
		template = cv2.imread('var/fishing_float_' + str(x) + '.png', 0)
		# print('template',template)
		# 读取图像
		img_rgb = cv2.imread(img_name)
		# BGR2GRAY
		img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
		# cv2.imwrite('grayed.png',img_gray)

		th,tw = template.shape[:2]
		result = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
		print('the'+str(x+1)+'time max_val is',max_val)
		if max_val>0.3 :
			tl = max_loc   #左上点
			br = (tl[0]+tw,tl[1]+th)    #右下点
			# print('zuoshagnjiao',tl)
			# print('youxiajiao',br)
			cv2.rectangle(img_gray,tl,br,(0,0,255),2)
			xx,xy = (br[0]-tl[0])/2+tl[0],(br[1]-tl[1])/2+tl[1]  #相对于算法计算中，float所在位置的中点
			return xx,xy
		else:
			return (300,100)





		# print('got images')
		# w, h = template.shape[::-1]     #对比样本template的宽高
		# print('template,w,h',w,h)
		# res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		# # print('res is',res)
		# threshold = 0.6
        #
		# loc = np.where( res >= threshold)
		# # print('loc is',loc)
		# for pt in zip(*loc[::-1]):
		#     cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
		# if loc[0].any():
		# 	print('Found ' + str(x) + ' float')
		# 	# print 'Found ' + str(x) + ' float'
		# 	if dev:
		# 		cv2.imwrite('var/fishing_session_' + str(int(time.time())) + '_success.png', img_rgb)
		# 	return (loc[1][0] + w / 2) / 2, (loc[0][0] + h / 2) / 2


def move_mouse(place):
	x,y = place[0], place[1]
	print("Moving cursor to " + str(place))
	# autopy.mouse.smooth_move(int(screen_start_point[0]) + x , int(screen_start_point[1]) + y)
	autopy.mouse.smooth_move(300 + x , 100 + y)
def listen():
	print('Well, now we are listening for loud sounds...')
	# print 'Well, now we are listening for loud sounds...'
	CHUNK = 1024  # CHUNKS of bytes to read each time from mic
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 18000
	THRESHOLD = 1200  # The threshold intensity that defines silence
	                  # and noise signal (an int. lower than THRESHOLD is silence).
	SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
	                   # only silence is recorded. When this time passes the
	                   # recording finishes and the file is delivered.
	#Open stream
	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
	                channels=CHANNELS,
	                rate=RATE,
	                input=True,
	                frames_per_buffer=CHUNK)
	cur_data = ''  # current chunk  of audio data
	rel = RATE/CHUNK
	# maxlen=SILENCE_LIMIT * rel
	# print('slid_win is',SILENCE_LIMIT * rel)
	# slid_win = deque(math.ceil(maxlen))
	# slid_win = deque.extend(range(math.ceil(maxlen)))
	slid_win = deque(maxlen=math.ceil(SILENCE_LIMIT * rel))
	success = False
	listening_start_time = time.time()
	while True:
		try:
			cur_data = stream.read(CHUNK)
			slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
			if(sum([x > THRESHOLD for x in slid_win]) > 0):
				print('I heart something!')
				# print 'I heart something!'
				success = True
				break
			if time.time() - listening_start_time > 20:
				print('I don\'t hear anything already 20 seconds!')
				# print 'I don\'t hear anything already 20 seconds!'
				break
		except IOError:
			break

	# print "* Done recording: " + str(time.time() - start)
	stream.close()
	p.terminate()
	return success

def snatch():
	print('Snatching!')
	# autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
	autopy.mouse.click(autopy.mouse.Button.RIGHT)
def logout():
	autopy.key.tap(autopy.key.Code.RETURN)
	time.sleep(0.1)
	for c in u'/logout':
		time.sleep(0.1)
		autopy.key.tap(c)
	time.sleep(0.1)

	autopy.key.tap(autopy.key.Code.RETURN)

def main():

	if check_process() and not dev:
		print("Waiting 2 seconds, so you can switch to WoW WoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoWWoW")
		# print "Waiting 2 seconds, so you can switch to WoW"
		time.sleep(2)

	check_screen_size()
	catched = 0
	tries = 0
	while not dev:
		tries += 1
		send_float()
		im = make_screenshot()
		place = find_float(im)
		print('the place is',place)
		if not place:
			print('Float was not found, retrying in 2 seconds')
			# print 'Float was not found, retrying in 2 seconds'
			time.sleep(3)
			im = make_screenshot()   #
			place = find_float(im)
			if not place:
				print('Still can\'t find float, breaking this session')
				# print 'Still can\'t find float, breaking this session'
				jump()
				continue
		print('Float found at ' + str(place))
		move_mouse(place)
		if not listen():
			print('If we didn\' hear anything, lets try again')
			# print 'If we didn\' hear anything, lets try again'
			jump()
			continue
		snatch()
		time.sleep(3)
		catched += 1
		print('I guess we\'ve snatched something')
		# print 'I guess we\'ve snatched something'
		if catched == 250:
			break
		time.sleep(3)
	print('catched ' + str(catched))
	# print 'catched ' + str(catched)
	logout()

main()
