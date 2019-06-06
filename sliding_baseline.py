import cv2
import os
import random
import time
import numpy as np

import image_processing


DIFF_METHOD = 1
ALPHA = 0.5
KERNEL = 11


def run_session(session=None, viz=False):
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    # create important databases
    baseline = cv2.imread(session_images[0])
    mask, history = image_processing.create_changes_dbs(baseline)

    #baseline = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    baseline = cv2.GaussianBlur(baseline, (KERNEL, KERNEL), 0)

    for i in range(1, len(session_images)):
        im1 = cv2.imread(session_images[i - 1])
        im2 = cv2.imread(session_images[i])
        im1 = cv2.GaussianBlur(im1, (KERNEL, KERNEL), 0)
        im2 = cv2.GaussianBlur(im2, (KERNEL, KERNEL), 0)

        # sliding baseline
        baseline = (1 - ALPHA) * baseline + ALPHA * im1

        print(baseline.shape)

        # Call diff method
        diff = image_processing.DIFF_METHODS[DIFF_METHOD](baseline.astype(np.uint8), im2.astype(np.uint8))

        # update changes
        mask, history = image_processing.update_changes(mask, history, diff)

        # Draw all the contours on the map
        output1 = image_processing.draw_changes(baseline.copy(), mask)
        output2 = image_processing.draw_changes(im2.copy(), mask)

        cv2.imwrite("demos/demo" + str(i) + ".jpg", output1)
        cv2.imwrite("results/result.jpg", output1)

        if viz:
            cv2.imshow("Difference ", output1.astype(np.uint8))
            cv2.waitKey(0)
            cv2.imshow("Difference ", output2)
            cv2.waitKey(0)
        else:
            time.sleep(1)

    # output the final differences
    output = cv2.imread(session_images[0])
    output = image_processing.draw_changes(output, image_processing.combine_masks(final_mask, mask))
    cv2.imwrite("demos/final.jpg", output)
    cv2.imshow("Output", output)
    cv2.waitKey(0)


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