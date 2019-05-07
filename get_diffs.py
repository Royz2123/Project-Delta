import cv2
import os
import random
import time

import image_processing


DIFF_METHOD = 1


def run_session(session=None, viz=True):
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    # create important databases
    baseline = cv2.imread(session_images[0])
    mask, history = image_processing.create_changes_dbs(baseline)

    for i in range(1, len(session_images)):
        baseline = cv2.imread(session_images[0])
        im = cv2.imread(session_images[i])

        # Call diff method
        diff = image_processing.DIFF_METHODS[DIFF_METHOD](baseline, im)

        # update changes
        mask, history = image_processing.update_changes(mask, history, diff)

        # Draw all the contours on the map
        output1 = image_processing.draw_changes(baseline, mask)
        output2 = image_processing.draw_changes(im, mask)

        cv2.imwrite("demos/demo" + str(i) + ".jpg", output1)
        cv2.imwrite("results/result.jpg", output1)

        if viz:
            cv2.imshow("Difference ", output1)
            cv2.waitKey(0)
            cv2.imshow("Difference ", output2)
            cv2.waitKey(0)
        else:
            time.sleep(1)

    # output the final differences
    output = cv2.imread(session_images[0])
    output = image_processing.draw_changes(output, mask)
    cv2.imwrite("demos/final.jpg", output)
    cv2.imshow("Output", output)
    cv2.waitKey(0)


if __name__ == "__main__":
    run_session("indoor")


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