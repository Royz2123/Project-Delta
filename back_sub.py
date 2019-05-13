import numpy as np
import cv2
import os

session_path = "sessions/indoor/"
session_images = [session_path + path for path in sorted(os.listdir(session_path))]

fgbgs = [
    cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=20, detectShadows=True),
    cv2.bgsegm.createBackgroundSubtractorGMG(),
    cv2.bgsegm.createBackgroundSubtractorLSBP(minCount=50000),
    cv2.bgsegm.createBackgroundSubtractorGSOC(),
    cv2.bgsegm.createBackgroundSubtractorCNT(),
]




for path in session_images:
    frame = cv2.imread(path, 0)
    frame = cv2.equalizeHist(frame)

    fgmask = fgbgs[2].apply(frame)
    cv2.imshow('frame', fgmask)
    k = cv2.waitKey(300) & 0xff
    if k == 27:
        break

    cv2.imshow('frame', fgmask)
    k = cv2.waitKey(300) & 0xff
    if k == 27:
        break
cv2.destroyAllWindows()