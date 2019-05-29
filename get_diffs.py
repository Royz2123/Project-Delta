import cv2
import os
import time
import numpy as np

import image_processing
import moviepy.editor as mp

from day_or_night import is_night_mode
from period_changes import Period

diff_method = image_processing.DiffMethods.INTERSECT


def create_video(path):
    w, h, d = cv2.imread(path + os.listdir(path)[0]).shape
    out = cv2.VideoWriter('./results/timelapse.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 7, (h, w))

    for file in os.listdir(path):
        filepath = path + file
        out.write(cv2.imread(filepath))
    out.release()
    cv2.destroyAllWindows()

    # create webm as well
    clip = mp.VideoFileClip("./results/timelapse.mp4")
    clip.write_videofile("./results/timelapse.webm")


def run_session(session=None, viz=True):
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    create_video(session_path)

    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    # create important databases
    baseline = cv2.imread(session_images[0])
    cv2.imwrite("./results/baseline.jpg", baseline)

    mask, history = image_processing.create_changes_dbs(baseline)
    final_mask = mask.copy()
    baseline_index = 0

    p = Period()

    for i in range(1, len(session_images)):
        baseline = cv2.imread(session_images[baseline_index])
        im = cv2.imread(session_images[i])
        if is_night_mode(im):
            print("skip (night)")
            continue
        # Call diff method
        diff = diff_method(baseline, im)

        # Check if reliable diff
        if not image_processing.reliable_baseline(diff):
            print("Unreliable diff")
            final_mask = image_processing.combine_masks(final_mask, mask)
            mask, history = image_processing.create_changes_dbs(baseline)

            # optimally, take another image immediately after
            baseline_index = i
            continue

        # update changes
        mask, history = image_processing.update_changes(mask, history, diff)
        p.add_diff(image_processing.combine_masks(final_mask, mask))
        period = p.get_period_changes()

        # Draw all the contours on the map
        output1 = image_processing.draw_changes(baseline, period*image_processing.combine_masks(final_mask, mask))
        output2 = image_processing.draw_changes(im, period*image_processing.combine_masks(final_mask, mask))

        cv2.imwrite("demos/demo" + str(i) + ".jpg", output1)
        cv2.imwrite("results/result.jpg", output1)

        if viz:
            # cv2.imshow("Difference ", output1)
            # k = cv2.waitKey(300) & 0xff
            # if k == 27:
            #     break
            cv2.imshow("Difference ", output2)
            k = cv2.waitKey(image_processing.IMAGE_SHOW_DELAY) & 0xff
            if k == 27:
                break
        else:
            time.sleep(1)

    # output the final differences
    output = cv2.imread(session_images[0])
    output = image_processing.draw_changes(output, image_processing.combine_masks(final_mask, mask))
    cv2.imwrite("demos/final.jpg", output)
    cv2.imshow("Output", output)
    cv2.waitKey(0)


if __name__ == "__main__":
    run_session("outdoor4")


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