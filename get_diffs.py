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


def update_gallery(path=None, day_index=0, hour_index=0):
    SAMPLES = 12
    if path is None:
        path = "sessions/" + max(os.listdir("sessions/")) + "/"

    images = sorted(os.listdir(path))

    data = {}
    for index, image in enumerate(images):
        day = "/".join(image.split(".")[0].split("_")[1:3])
        hour = ":".join(image.split(".")[0].split("_")[3:5])

        if day not in data:
            data[day] = []

        if index % SAMPLES == 0:
            data[day].append((hour, index))

    # plot the days
    s = "<div class='gallerymargin'><ul class='gallery'>"
    chosen_date = ""
    for i, date in enumerate(data):
        if i == day_index:
            chosen_date = date
            s += '<li><a class="active" href="/gallery.html?day=%d&hour=%d">%s</a></li>' % (i, hour_index, date)
        else:
            s += '<li><a href="/gallery.html?day=%d&hour=%d">%s</a></li>' % (i, hour_index, date)
    s += "</ul></div>"

    # plot the hours
    s += "<ul class='gallery'>"
    chosen_hour = ""
    for i, (hour, index) in enumerate(data[chosen_date]):
        if i == hour_index:
            chosen_hour = hour
            s += '<li><a class="active" href="/gallery.html?day=%d&hour=%d">%s</a></li>' % (day_index, i, hour)
        else:
            s += '<li><a href="/gallery.html?day=%d&hour=%d">%s</a></li>'% (day_index, i, hour)
    s += "</ul>"

    # plot the images
    s += '<div class="row">\n'
    index = dict(data[chosen_date])[chosen_hour]
    for i, file in enumerate(images[index : index + SAMPLES]):
        if i % 4 == 0:
            if i != 0:
                s +='</div></div>\n'
            s += '<div class="row"><div>\n'
        filepath = path + file
        s += '<div class="gallery"><img width="20%%" height="125" src=/%s onclick="location.href=\'/%s\'">\n' % (filepath, filepath)
        s += '<div class="desc">%s</div></div>' % file.split(".")[0].replace("_", " ")
    s += '</div></div>\n'

    page_content = ""
    with open("./templates/gallery.html", "r") as fileobj:
        page_content = fileobj.read()

    with open("./templates/gallery.html", "w") as fileobj:
        lst = page_content.split("<!--EYECATCHER-->")
        lst[1] = s
        fileobj.write("<!--EYECATCHER-->".join(lst))


def run_session(session, viz=False):
    print(viz)
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    # create_video(session_path)
    update_gallery(session_path)

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
        orig = im.copy()
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

        cv2.imwrite("demos/demo" + str(i) + ".jpg", output2)
        cv2.imwrite("results/result.jpg", output2)
        cv2.imwrite("results/last.jpg", orig)

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
    #cv2.imshow("Output", output)
    #cv2.waitKey(0)


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