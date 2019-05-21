import cv2
import os
import time

import image_processing

from day_or_night import is_night_mode


diff_method = image_processing.DiffMethods.INTERSECT


def run_session(session=None, viz=True):
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    # create important databases
    baseline = cv2.imread(session_images[0])
    cv2.imwrite("./results/baseline.jpg", baseline)

    mask, history = image_processing.create_changes_dbs(baseline)
    final_mask = mask.copy()
    baseline_index = 0

    for i in range(1, len(session_images)):
        baseline = cv2.imread(session_images[baseline_index])
        im = cv2.imread(session_images[i])
        if is_night_mode(im):
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

        # Draw all the contours on the map
        output1 = image_processing.draw_changes(baseline, image_processing.combine_masks(final_mask, mask))
        output2 = image_processing.draw_changes(im, image_processing.combine_masks(final_mask, mask))

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