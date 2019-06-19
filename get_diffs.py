import cv2
import os
import time
import numpy as np
import random

import image_processing
# import moviepy.editor as mp

from day_or_night import is_night_mode
from period_changes import Period
import create_session

diff_method = image_processing.DiffMethods.INDOOR
TIMELAPSE_SECONDS = 500


def create_video(path):
    h, w, d = cv2.imread(path + os.listdir(path)[0]).shape
    out = cv2.VideoWriter('./results/timelapse.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 15, (w, h))

    for file in os.listdir(path):
        filepath = path + file
        out.write(cv2.imread(filepath))
    out.release()
    cv2.destroyAllWindows()

    # create webm as well
    # clip = mp.VideoFileClip("./results/timelapse.mp4")
    # clip.write_videofile("./results/timelapse.webm")
    os.remove("./results/timelapse.webm")
    os.system("ffmpeg-win64-v4.1 -i ./results/timelapse.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -b:a 128k -c:a libopus ./results/timelapse.webm")


def update_gallery(path="./sessions/current_session/", day_index=0, hour_index=0):
    SAMPLES = 12
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
            s += '<li><a class="active" href="/gallery.html?day=%d&hour=%d&rand=%f">%s</a></li>' % (i, hour_index, random.random(), date)
        else:
            s += '<li><a href="/gallery.html?day=%d&hour=%d&rand=%f">%s</a></li>' % (i, hour_index, random.random(), date)
    s += "</ul></div>"

    # plot the hours
    s += "<ul class='gallery'>"
    chosen_hour = ""
    for i, (hour, index) in enumerate(data[chosen_date]):
        if i == hour_index:
            chosen_hour = hour
            s += '<li><a class="active" href="/gallery.html?day=%d&hour=%d&rand=%f">%s</a></li>' % (day_index, i, random.random(), hour)
        else:
            s += '<li><a href="/gallery.html?day=%d&hour=%d&rand=%f">%s</a></li>' % (day_index, i, random.random(), hour)
    s += "</ul>"

    # plot the images
    s += '<div class="row">\n'
    index = dict(data[chosen_date])[chosen_hour]
    for i, file in enumerate(images[index: index + SAMPLES]):
        if i % 4 == 0:
            if i != 0:
                s += '</div></div>\n'
            s += '<div class="row"><div>\n'
        filepath = path + file
        s += '<div class="gallery"><img width="20%%" height="125" src=/%s onclick="location.href=\'/%s\'">\n' % (
        filepath, filepath)
        s += '<div class="desc">%s</div></div>' % file.split(".")[0].replace("_", " ")
    s += '</div></div>\n'

    page_content = ""
    with open("./templates/gallery.html", "r") as fileobj:
        page_content = fileobj.read()

    with open("./templates/gallery.html", "w") as fileobj:
        lst = page_content.split("<!--EYECATCHER-->")
        lst[1] = s
        fileobj.write("<!--EYECATCHER-->".join(lst))


def run_session(viz=False):
    # run_session_try(viz)
    while True:
        try:
            run_session_try(viz)
        except Exception as e:
            print("Error in get_diffs, Running again: ", e)


def run_session_try(viz=False):
    session_path = "./sessions/current_session/"

    while True:
        if len(os.listdir(session_path)):
            create_video(session_path)
            last_video = time.time()

            # create important databases
            min_path = min(os.listdir(session_path))
            min_path = os.path.join(session_path, min_path)

            baseline = cv2.imread(min_path)
            cv2.imwrite("./results/baseline.jpg", baseline)
            break

        else:
            print("No images yet")
            time.sleep(2)

    mask, history = image_processing.create_changes_dbs(baseline)
    final_mask = mask.copy()
    baseline_index = 0

    p = Period()

    while True:
        time.sleep(1)
        update_gallery()

        max_path = max(os.listdir(session_path))
        min_path = min(os.listdir(session_path))
        max_path = os.path.join(session_path, max_path)
        min_path = os.path.join(session_path, min_path)

        if time.time() - last_video > TIMELAPSE_SECONDS:
            print("Creating Timelapse, Pausing Program")
            create_video(session_path)
            last_video = time.time()

        baseline = cv2.imread(min_path)
        cv2.imwrite("./results/baseline.jpg", baseline)

        im = cv2.imread(max_path)
        orig = im.copy()

        diff = diff_method(baseline, im)

        # update changes
        mask, history = image_processing.update_changes(mask, history, diff)
        p.add_diff(image_processing.combine_masks(final_mask, mask), max_path)
        period = p.get_period_changes(enable=False)

        # Draw all the contours on the map
        output1 = image_processing.draw_changes(baseline, period * image_processing.combine_masks(final_mask, mask))
        output2 = image_processing.draw_changes(im, period * image_processing.combine_masks(final_mask, mask))

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
            time.sleep(0.05)

    # output the final differences
    # output = cv2.imread(session_images[0])
    # output = image_processing.draw_changes(output, image_processing.combine_masks(final_mask, mask))
    # cv2.imwrite("demos/final.jpg", output)
    # cv2.imshow("Output", output)
    # cv2.waitKey(0)


def run_session_old(session, viz=False):
    print(viz)
    # Choose session (latest vs. specific)
    if session is None:
        session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    else:
        session_path = "sessions/" + session + "/"

    create_video(session_path)
    last_video = time.time()

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
        if time.time() - last_video > TIMELAPSE_SECONDS:
            print("Creating Timelapse, Pausing Program")
            create_video(session_path)

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
        p.add_diff(image_processing.combine_masks(final_mask, mask), sorted(os.listdir(session_path))[i])
        period = p.get_period_changes(enable=False)

        # Draw all the contours on the map
        output1 = image_processing.draw_changes(baseline, period * image_processing.combine_masks(final_mask, mask))
        output2 = image_processing.draw_changes(im, period * image_processing.combine_masks(final_mask, mask))

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
            time.sleep(0.05)

    # output the final differences
    # output = cv2.imread(session_images[0])
    # output = image_processing.draw_changes(output, image_processing.combine_masks(final_mask, mask))
    # cv2.imwrite("demos/final.jpg", output)
    # cv2.imshow("Output", output)
    # cv2.waitKey(0)


if __name__ == "__main__":
    run_session("z_outdoor4")

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
