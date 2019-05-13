import numpy as np
import cv2 as cv
cap = cv.VideoCapture('Project-Delta/videos/1.mp4')
fgbg = cv.bgsegm.createBackgroundSubtractorLSBP(minCount=1, LSBPthreshold=10, Tlower=10, Tupper=20)
i = 0
while(1):
    ret, frame = cap.read()
    print(frame)
    i += 1
    if i % 10 == 0:
        fgmask = fgbg.apply(frame, learningRate=1)
        cv.imshow('frame',frame)
        k = cv.waitKey(300) & 0xff
        if k == 27:
            break
        i = 0
cap.release()
cv.destroyAllWindows()