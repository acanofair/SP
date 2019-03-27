import cv2, time, pandas, json, argparse, imutils
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera


#Argument to set the min area of motion detection
#To start python ProgramName.py -a Area  
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area" , type= int, default=500, help="min area size")
args = vars(ap.parse_args())




camera = cv2.VideoCapture(-1)
background = None
motion = [None, None]
time = []
rw = PiRGBArray(camera, size=tuple([649, 480]))
fourcc = cv2.cv.CV_FOURCC(* 'XVID')
capper = cv2.VideoWriter('out.avi', fourcc, 20.0, (640,480))


#Initialization of dataframe
df = pandas.DataFrame(columns = ["Start","Stop"])

while  True:
    check, frame = camera.read()
    motion = 0
    
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
    
    for c in cnts:
        if cv2.contourArea(c) < 10000:
            continue
        
        motion += 1
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y) , (x+w, y+h), (255, 0, 0), 2)
        text="Motion"
        cv2.putText(frame, "Status: {} ".format(text), (10,20), cv2.FONT_HERSHEY_PLAIN, 0.5, (0,0, 255) ,2)
        
        if text == "Motion":
            ret,yeet = camera.read()
            if ret: 
                capper.write(yeet)
            else:
                break
            got = "Boys we got'em"
            cv2.putText(frame, "Status: {} ".format(got), (10,20), cv2.FONT_HERSHEY_PLAIN, 0.5, (0,0, 255) ,2)
        else:
            break
            


    cv2.imshow("Camera Stream", frame)
    cv2.waitKey(1)
    
    
camera.release()
capper.release()
cv2.destoryAllWindows()
