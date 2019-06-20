import camera_api
import time
import cv2
import os
import datetime
from time import gmtime, strftime
import shutil

import util

def get_curr_time():
    return strftime("%Y_%m_%d_%H_%M_%S", gmtime())


WAIT_TIME = 180
FOLDER_NAME = "./sessions/current_session/"
RESULTS_NAME = "./results/"


def clean_up():
    # remove session
    for file in os.listdir(FOLDER_NAME):
        os.remove(os.path.join(FOLDER_NAME, file))

    # remove results
    for file in os.listdir(RESULTS_NAME):
        os.remove(os.path.join(RESULTS_NAME, file))

    # remove credentials
    util.set_creds("", "")


def main():
    while True:
        creds = util.get_creds()

        if creds[0] == "":
            # print("No login")
            time.sleep(3)
            continue

        curr_im = camera_api.get_snapshot()
        cv2.imwrite(FOLDER_NAME + get_curr_time() + ".jpg", curr_im)
        # print("Took screenshot")

        # wait between images
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()


"""
    last_im = camera_api.get_snapshot()

    cv2.imshow("preview", curr_im)

    diff = cv2.absdiff(last_im, curr_im)
    cv2.imshow("Difference", diff)

    # next iteration
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    last_im = curr_im
"""