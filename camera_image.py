#This code captures the images and save it to the file with the name smart_cap.png
#in the same folder

import cv2
import time
import sys
import signal
 
# You might need to change to the right camera, it is required by cv2.videocapture
camera_port = 0
 
#Number of frames to throw away while the camera adjusts to light levels
ramp_frames = 30
display = "Display Window"
file = "smart_cap.png"

#To handle the SIGINT when CTRL+C is pressed
def exit_gracefully(signum,frame):
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(1)
 

# Captures a single image from the camera
def get_image(camera):
    retval, im = camera.read()
    return im

def take_save_image(camera): 
    # Take the actual image we want to keep
    camera_capture = get_image(camera)
    # A nice feature of the imwrite method is that it will automatically choose the
    # correct format based on the file extension you provide. Convenient!
    cv2.imwrite(file, camera_capture)
    #cv2.imshow(display, camera_capture)
 

def run_main():
    # First initialize the camera capture object with the cv2.VideoCapture class.
    camera = cv2.VideoCapture(camera_port)
    
    #To create a new window for display
    #Disabled it for now as we can't see the image on the cap
    #cv2.namedWindow(display, cv2.WINDOW_NORMAL)	

    # Discard the first few frame to adjust the camera light levels
    for i in xrange(ramp_frames):
        temp = get_image(camera)

    #Now take the image and save it after every 1 second
    while(1):
        try:
            time.sleep(1)
            take_save_image(camera)
        except Exception, e:
            print "Exception occured \n"
            print e
            pass 

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT,exit_gracefully)
    run_main()
