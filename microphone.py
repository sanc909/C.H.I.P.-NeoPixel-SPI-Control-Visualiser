import time
import numpy as np
import pyaudio
import config
import led
import threading

""" SC added 12OCT2017 - amended to remove exception_on_overflow so that CHIP works. """ 

def start_stream(callback,*args):
    p = pyaudio.PyAudio()
    frames_per_buffer = int(config.MIC_RATE / config.FPS)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=config.MIC_RATE,
                    input=True,
                    frames_per_buffer=frames_per_buffer)
    overflows = 0
    prev_ovf_time = time.time()
    t = threading.currentThread()
    while getattr(t, "mic_on", True):
        try:
# ORIGINAL  y = np.fromstring(stream.read(frames_per_buffer,exception_on_overflow = False), dtype=np.int16)
            y = np.fromstring(stream.read(frames_per_buffer), dtype=np.int16)
            y = y.astype(np.float32)
            callback(y,*args)
        except IOError:
            overflows += 1
#            if time.time() > prev_ovf_time + 1:
#               prev_ovf_time = time.time()
#            print('Audio buffer has overflowed {} times'.format(overflows))

    stream.stop_stream()
    stream.close()
    p.terminate()
