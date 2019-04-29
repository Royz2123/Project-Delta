import cv2
import os
import random
import time

import image_processing


DIFF_METHOD = 1
MOVEMENT_THRESH = 0.7

VIZ_MODE = 0

def compare_cnts(cnt1, cnt2):
    equal_count = 0
    for value in cnt1:
        if any([value[0][0] == coord[0][0] and value[0][1] == coord[0][1] for coord in cnt2]):
            equal_count += 1
    return equal_count


# Class that represents the suspicious item
class SuspiciousItem(object):
    # If item has been in frame for MIN_STEPS, keep until end of run
    MIN_STEPS = 100

    # If item has been spotted in MIN_RATIO frames, keep currently
    MIN_RATIO = 0.3

    def __init__(self, cnt):
        self._cnt = cnt
        self._stayed = 1
        self._moved = 0
        self._id = random.randint(1, 100)

    def ratio(self):
        return self._stayed / (self._stayed + self._moved)

    def keep_item(self):
        if self._stayed > SuspiciousItem.MIN_STEPS or self.ratio() > SuspiciousItem.MIN_RATIO:
            return True
        return False

    def get_contour(self):
        return self._cnt

    def __eq__(self, other):
        equal_count = compare_cnts(self._cnt, other._cnt)
        return equal_count > (min(len(self._cnt), len(other._cnt)) / 2)

    def update_item_status(self, stay):
        if stay:
            self._stayed += 1
        else:
            self._moved += 1

    def __str__(self):
        return "Item %d. Ratio: %s, Size: %d" % (self._id, self.ratio(), len(self._cnt))



def run_session():
    session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    suspicious_items = []

    for i in range(len(session_images) - 1):
        im1 = cv2.imread(session_images[i])
        im2 = cv2.imread(session_images[i+1])

        #cv2.imshow("Difference ", im1)
        #cv2.waitKey(0)
        #cv2.imshow("Difference ", im2)
        #cv2.waitKey(0)

        # Call diff method
        diff = image_processing.DIFF_METHODS[DIFF_METHOD](im1, im2)
        cnts = image_processing.get_contours(diff)

        # Add the new contours to the list of suspicious items
        for cnt in cnts:
            curr_item = SuspiciousItem(cnt)
            if not any([curr_item == item for item in suspicious_items]):
                suspicious_items.append(curr_item)

        # check which contours stayed from last time
        new_items = []
        for item in suspicious_items:
            item_movement = image_processing.contour_stayed(im1, im2, item.get_contour())
            item.update_item_status(item_movement < MOVEMENT_THRESH)
            if item_movement > MOVEMENT_THRESH:
                print("Item moved!", item)
            if item.keep_item():
                new_items.append(item)
        suspicious_items = new_items

        # Draw all the contours on the map
        curr_cnts = [item.get_contour() for item in suspicious_items]
        output1 = image_processing.draw_rect_contours(im1, curr_cnts)
        output2 = image_processing.draw_rect_contours(im2, curr_cnts)

        cv2.imwrite("demos/demo" + str(i) + ".jpg", output1)
        cv2.imwrite("results/result.jpg", output1)

        if VIZ_MODE:
            cv2.imshow("Difference ", output1)
            cv2.waitKey(0)
            cv2.imshow("Difference ", output2)
            cv2.waitKey(0)
        else:
            time.sleep(1)

    # output the final differences
    output = cv2.imread(session_images[0])
    output = image_processing.draw_rect_contours(output, [item.get_contour() for item in suspicious_items])
    cv2.imwrite("demos/final.jpg", output)
    cv2.imshow("Output", output)
    cv2.waitKey(0)


if __name__ == "__main__":
    run_session()


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