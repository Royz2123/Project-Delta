import numpy as np
import cv2
import os

session_path = "sessions/outdoor/"
session_images = [session_path + path for path in sorted(os.listdir(session_path))]

cap = cv2.VideoCapture('vtest.avi')
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

for path in session_images:
    frame = cv2.imread(path)
    fgmask = fgbg.apply(frame)
    cv2.imshow('frame', fgmask)
    k = cv2.waitKey(300) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()