
from LightWeightMotion.LWMI import LightWeightInitial 
from imutils.video import VideoStream
import argparse,datetime,imutils,time,cv2,os, glob
from picamera.array import PiRGBArray
from picamera import PiCamera



fourcc = cv2.VideoWriter_fourcc(* 'DIVX')

print("Taking capture and beginning stream")
camera = VideoStream(-1).start()
time.sleep(2.0)

lightmo = LightWeightInitial(32)
consecFrames = 0

print consecFrames
nonmovementframe = 0
fps = 20.0 
background = None 
rw = PiRGBArray(camera, size=tuple([649, 480]))
dropboxupload = "/home/pi/Deskotp/dropbox_uploader.sh upload"
name = str(datetime.datetime.now()) 

def sendtobox(name):
    os.system("/home/pi/Desktop/dropbox_uploader.sh upload /home/pi/Desktop/tempvid/ "  + name)
    
#def clearfold(foldername):
    
    
while True:
    
    frame = camera.read()
    frame = imutils.resize(frame, width=600)
    
    updateConsecFrames = True
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0 )

    if background is None:
        background = gray.copy()
        b = gray.copy().astype("float")
        rw.truncate(0)
        continue

    difference = cv2.absdiff(background,gray)
    cv2.accumulateWeighted(gray, b, 0.5)
    df = cv2.absdiff(gray, cv2.convertScaleAbs(b))
    tf = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)[1]
    tf = cv2.dilate(tf, None, iterations = 2)

    cnts = cv2.findContours(tf.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
   
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        (x,y,w,h) = cv2.boundingRect(c)
        updateConsecFrames = h <= 10

        
        if h > 10:
            consecFrames = 0
            cv2.rectangle(frame, (x,y) , (x+w, y+h), (255, 0, 0), 2)
            if not lightmo.recording:
                timestamp = datetime.datetime.now()
                
#                name = "{}/{}.avi".format( "/home/pi/Desktop/tempvid ", timestamp.strftime("%Y%m%d-%H%M%S"))
                name = "/home/pi/Desktop/tempvid/" + str(datetime.datetime.now()) + '.avi'.format("/home/pi/Desktop/tempvid")
                lightmo.start(name,fourcc,fps)
                if consecFrames == 0:
                    lightmo.sendtobox() 
                
       
                
                

    if updateConsecFrames:
        consecFrames += 1

    lightmo.update(frame)
    

    if lightmo.recording and consecFrames == 64:
        lightmo.finish()

        
#    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
  
    if key == ord("q"):

        break

if lightmo.recording:
    lightmo.finish()
    
#if not lightmo.recording:
#    

cv2.destroyAllWindows()
camera.stop()
