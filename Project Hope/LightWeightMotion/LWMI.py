#!/usr/bin/env python
from collections import deque
from threading import Thread
from multiprocessing import Queue
import datetime
import time
import cv2
import glob
import os 


class LightWeightInitial:
    def __init__ (self, bufSize = 64, timeout = 1.0):
        self.bufSize = bufSize
        self.timeout = timeout
        self.frames = frame = deque(maxlen=bufSize)
        self.capper = None
        self.thread = None
        self.Q = None
        self.name = str(datetime.datetime.now())
        self.recording = False
        self.path = glob.glob("/home/pi/Desktop/tempvid/*.avi  ")
        
    def update(self, frame):
        self.frames.appendleft(frame)
        
        if self.recording:
            self.Q.put(frame)
            
    def start(self, outpath, fourcc, fps):
        self.recording = True
        self.capper = cv2.VideoWriter(outpath, fourcc, fps,
            (self.frames[0].shape[1], self.frames[0].shape[0]), True)
        self.Q = Queue()
        
        for i in range(len(self.frames), 0, -1):
            self.Q.put(self.frames[i-1])
                       
        self.thread = Thread(target=self.write, args=())
        self.thread.daemon = True
        self.thread.start()
    
    def write(self):
        while True:
            if not self.recording:
                return
            
            if not self.Q.empty():
                frame = self.Q.get()
                self.capper.write(frame)
            else:
                time.sleep(1.0)

    def flush(self):
        while not self.Q.empty():
            frame = self.Q.get()
            self.capper.write(frame)
            
    def finish(self):
        self.recording = False
        self.thread.join()
        self.flush()
        self.capper.release()
        
    def cleanup(self):
        os.remove(self.path)
    
    def sendtobox(self):
        os.system("/home/pi/Desktop/dropbox_uploader.sh upload /home/pi/Desktop/tempvid/ "  + self.name)
#        foldername = glob.glob("/home/pi/Desktop/tempvid/*.avi  ")
