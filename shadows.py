import cv2
import numpy as np
import os
import datetime

def diff(img1, img2):
    hsv1 = cv2.cvtColor(img1,cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
    d = cv2.absdiff(hsv1, hsv2)
    d = cv2.absdiff(hsv1, hsv2)
    cv2.imshow("boop", d)

    hp = 1/(0.05*hsv2[:,:,2]+1)
    hsv2[:, :, 0] = hp * hsv1[:, :, 0] + (1 - hp) * hsv2[:, :, 0]
    sp = 1/(0.05*hsv2[:,:,2]+1)
    hsv2[:, :, 1] = sp * hsv1[:, :, 1] + (1 - sp) * hsv2[:, :, 1]
    vp = 1/(0.05*hsv2[:,:,2]+1)
    hsv2[:,:,2] = vp*hsv1[:,:,2]+(1-vp)*hsv2[:,:,2]



    tmp = cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)
    cv2.imshow("new",tmp)
    cv2.imshow("old", img2)
    cv2.imshow("origin", img1)

    new = cv2.cvtColor(tmp,cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)

    cv2.imshow("diff",cv2.absdiff(gray,new))


if __name__ == '__main__':
    # img1 = cv2.imread("C:\\Users\\t8545914\\Desktop\\my_projects\\Diff Finder\\Project-Delta\\sessions\\session_2019_05_28_09_15_52\\2019_05_28_12_55_46.jpg")
    # img2 = cv2.imread("C:\\Users\\t8545914\\Desktop\\my_projects\\Diff Finder\\Project-Delta\\sessions\\session_2019_05_28_09_15_52\\2019_05_28_14_26_45.jpg")
    # diff(img1,img2)
    # day_comparasone("C:\\Users\\t8545914\\Desktop\\my_projects\\Diff Finder\\Project-Delta\\sessions\\session_2019_05_28_09_15_52",1)
    # k = cv2.waitKey(0)
    # cv2.destroyAllWindows()
    pass