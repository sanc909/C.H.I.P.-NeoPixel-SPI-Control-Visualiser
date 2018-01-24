#!/usr/bin/env python
#####################################################################################
# A controller for neopixels.
# Video at https://www.youtube.com/watch?v=m9ATuX6nQkU 
# Inspired by and extended from Scott Lawson's excellent audio-reactive-led-Strip 
# to support next thing Co's C.H.I.P board 
#
# This is the controller script that offers a webpage to allow user to select
#
# Mood  - set fixed colour and number of Leds
# Meter - a simple peak level meter
# Music - Offers the original audio-reactive-strip  visualisations
#         Energy, Scroll or Spectrum 
# Off   - turn Led Strip off
# 
# This versions offers increased functionality:
# 1. Uses python flask to offer a webpage
# 2. Webpage allows user to select option and configuration
# 3. C.H.I.P uses SPI for connection to neopixel Led Strip. 
#
# Uses Chip's TRRS as mic-in so audio input to Alsa. 
# Chip in video 
# Assumes CHIP is configuted to connect to wifi via say nmtui
# Needs Python, python flask installed on CHIP.
# Needs SPI configured on CHIP - http://www.chip-community.org/index.php/SPI_support 
# Once Configured, test with daniperron's test script - https://bbs.nextthing.co/t/neopixel-stick-works-well-with-the-spi/15934 
# I found a small in-line amp to increase/decrease volume level helped processing.
# 
#
# Directory structure
# ChipNeoPixelController.py - main script, run this to launch webpage
# config.py - configuration settings for visualisation script
# visualisation.py - the visualisation script  which uses 
# dsp.py, gamma_table.py. gui.py, led.py, melbank.py, microphone.py, multithreading.py
# /templates/ directory contains
#    index.html - the webpage, CSS and 
#
# Scripts amended to support CHIP where appropriate. 
#
#####################################################################################

from flask import Flask, render_template, request   
from flask_wtf import Form
from led import getRGBWord
import config
from numpy import mean, sqrt, square
import numpy as np
import spidev
import time
import microphone
import visualization 
import math
import pyaudio

import threading
import time
# CHIP uses SPI... 
spi = spidev.SpiDev(32766,0)
spi.max_speed_hz=3000000

peak = 0 
dot=0
prev_buf = []
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
thread =  threading.Thread()
meterLeds=0
#
# Meter Option utility function to show level and animate a peak level indicator
# peak level slowly falls back to current level. 
# meter is red, peak is green.
def vu_meter(audio_samples,numLeds):
   # can start at edges or center, specified in form. 
   global peak, dot, prev_buf
   
   # get audio high and low    
   max=np.max(np.abs(audio_samples))                
   min=np.min(np.abs(audio_samples))
   PeakToPeak = max - min                           
   
   # scale value to number of LEDs in strip
   ledPos = int(np.interp(PeakToPeak,[0,1024],[0,numLeds/2]))  
   
   #clear
   r = [getRGBWord(0)]*config.N_PIXELS
   g = [getRGBWord(0)]*config.N_PIXELS
   b = [getRGBWord(0)]*config.N_PIXELS
   buf  =  [0,0,0, 0,0,0, 0,0,0, 0,0,0]
   buf  += np.hstack((g,r,b)).ravel().tolist()
   spi.xfer2(buf, spi.max_speed_hz,0,8)
   
   #left display in red
   r[0:ledPos] = [getRGBWord(1)]* (ledPos)
   g[0:ledPos] = [getRGBWord(0)]* (ledPos)
   b[0:ledPos] = [getRGBWord(0)]* (ledPos)

   howManyLeds = numLeds-ledPos 

   #right display in red
   r[howManyLeds:numLeds] = [getRGBWord(1)]* (ledPos)
   g[howManyLeds:numLeds] = [getRGBWord(0)]* (ledPos)
   b[howManyLeds:numLeds] = [getRGBWord(0)]* (ledPos)
   
   buf  =  [0,0,0, 0,0,0, 0,0,0, 0,0,0]
   buf  += np.hstack((g,r,b)).ravel().tolist()
   
   if not  np.array_equal(buf,prev_buf):
    spi.xfer2(buf, 3000000,0,8)
    prev_buf = buf

   if ledPos in range(1,numLeds/2) and ledPos > peak: 
     peak = ledPos 
   else:
     dot=dot+1
     if dot>= 4:
       if peak>0: 
         peak = peak-1
       dot = 0 
    
 
   #Right peak in green
   buf[peak*12+0] = getRGBWord(20)[0]
   buf[peak*12+1] = getRGBWord(20)[1]
   buf[peak*12+2] = getRGBWord(20)[2]
   buf[peak*12+3] = getRGBWord(0)[3]     

   #left peak in green
   buf[(numLeds-peak)*12+0] = getRGBWord(20)[0]
   buf[(numLeds-peak)*12+1] = getRGBWord(20)[1]
   buf[(numLeds-peak)*12+2] = getRGBWord(20)[2]
   buf[(numLeds-peak)*12+3] = getRGBWord(0)[3]     
    # Send to Neopixels 
   spi.xfer2(buf, 3000000,0,8)
   return
# 
# Mood  Option - light user specified number of neopixels in chosen colour
# 
 def Mood():
    Off()

    spi.max_speed_hz=3000000

    # get red,green and blue from web form  as ints 
    red      = int(request.form['Red'])   
    green    = int(request.form['Green'])
    blue     = int(request.form['Blue']) 
    moodLeds = int(request.form['MoodLeds'])

    # setup the leds
    r = [getRGBWord(red)  ]* moodLeds
    g = [getRGBWord(green)]* moodLeds
    b = [getRGBWord(blue) ]* moodLeds
    
    # add leading zero to get it to work
    buf = [0,0,0,0, 0,0,0,0, 0,0,0,0]+ np.hstack((g,r,b)).ravel().tolist()
    spi.xfer2(buf, spi.max_speed_hz,0,8)
# 
# Meter option -  start a daemon to display peak levels across a user specified number of leds
# 
 def Meter():
#   t1 = ThreadingExample(target=microphone.start_stream(vu_meter))
    global thread 
    meterLeds = int(request.form['MeterLeds'])

    thread = threading.Thread(target=microphone.start_stream,args=(vu_meter,meterLeds))
    thread.daemon = True                            # Daemonize thread
    thread.start()                                  # Start the execution
# 
# Music option -  start a daemon to display selected visualisation
# 
def Music(): 
    global thread 
    # Get Options
    viz_effect= request.form['VizEffect']
    min_Freq  = int(request.form['MinFreq'])
    max_Freq  = int(request.form['MaxFreq'])
    FFT_Bins  = int(request.form['FFTBins'])
    vizLeds   = int(request.form['VizLeds'])

    print("before viz thread start", viz_effect, min_Freq,max_Freq,FFT_Bins,vizLeds)

    #Start Daemon 
    thread = threading.Thread(target=microphone.start_stream,args=(visualization.microphone_update,vizLeds,viz_effect,min_Freq,max_Freq,FFT_Bins,))
    thread.daemon = True                            # Daemonize thread
    thread.start()                                  # Start the execution
# 
# Off option - turn off all Leds in strip
# 
def Off(): 
    r = [getRGBWord(0)]*config.N_PIXELS
    g = [getRGBWord(0)]*config.N_PIXELS
    b = [getRGBWord(0)]*config.N_PIXELS
    buf  =  [0,0,0, 0,0,0, 0,0,0, 0,0,0]
    buf  += np.hstack((g,r,b)).ravel().tolist()
    spi.xfer2(buf, spi.max_speed_hz,0,8)
# 
# Work out which Option has been selected
#   
options = {
   'Mood' : Mood,
   'Meter': Meter,
   'Music': Music,
   'Off'  : Off,
}
# 
# Display webpage in templates/index.html
# 
@app.route('/')
def index():
    return render_template('index.html',Red="12", Green="0",Blue="0",MoodLeds="30",MeterLeds="72",MinFreq="2000",MaxFreq="20000", FFTBINS="20" )
# 
# Process the submitted form 
# 
@app.route('/', methods=['POST','GET'])
def handle_data():
    Off()    
   
    for t in threading.enumerate():
      if t.name == "MainThread": 
         continue
# Stops microphone         
      t.mic_on  = False      
# get values from submitted form    
    choice    = request.form['Choice']
    red       = request.form['Red']
    green     = request.form['Green']
    blue      = request.form['Blue'] 
    moodLeds  = request.form['MoodLeds']
    meterLeds = request.form['MeterLeds']
    viz_effect= request.form['VizEffect']
    min_Freq  = request.form['MinFreq']
    max_Freq  = request.form['MaxFreq']
    FFT_Bins  = request.form['FFTBins']
    vizLeds   = request.form['VizLeds']

    peak = 0
    options[choice]() 
    return render_template('index.html',Red=red, Green=green,Blue=blue,MoodLeds=moodLeds,MeterLeds=meterLeds,MinFreq=min_Freq,MaxFreq=max_Freq,FFTBins=FFT_Bins,VizLeds=vizLeds,vizEffect=viz_effect)
#    return render_template('index.html')
    
#starts the python webpage
if __name__ == '__main__':
    app.run(host='0.0.0.0')

