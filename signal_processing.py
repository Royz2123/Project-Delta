import cv2
import os
import random
import time
import numpy as np

import image_processing



def run_session(session=None, viz=True):
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    # create important databases
    F = []
    F.append(cv2.imread(session_images[0]))
    F[0] = cv2.cvtColor(F[0], cv2.COLOR_BGR2GRAY)
    F[0] = cv2.GaussianBlur(F[0], (25, 25), 0)

    height, width = F[0].shape
    Q = [F[0].copy().astype(np.int32)]

    S = [np.zeros((height, width), np.int32)]

    for i in range(1, len(session_images) - 1):
        F.append(cv2.imread(session_images[i]))
        F[i] = cv2.cvtColor(F[i], cv2.COLOR_BGR2GRAY)
        F[i] = cv2.GaussianBlur(F[i], (25, 25), 0)

        # Check if reliable diff
        df = F[i].astype(np.int32) - F[i-1].astype(np.int32)

        # find signals
        ds = df.copy()
        ds[np.absolute(df) < 30] = 0
        #ds[np.absolute(df) >= 50] = 255
        dq = df - ds

        # update
        Q.append(Q[i-1] + dq)
        S.append(S[i-1] + ds)

        if viz:
            cv2.imshow("Difference ", F[i])
            cv2.waitKey(0)
            #cv2.imshow("Difference ", S[i])
            # cv2.waitKey(0)
        else:
            time.sleep(1)

    # output the final differences


if __name__ == "__main__":
    run_session("outdoor2")


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