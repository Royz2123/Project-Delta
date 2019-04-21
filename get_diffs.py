import cv2
import os

import image_processing


DIFF_METHOD = 0
SIMILARITY_THRESH = 0.5


# Class that represents the suspicious item
class SuspiciousItem(object):
    # If item has been in frame for MIN_STEPS, keep until end of run
    MIN_STEPS = 100

    # If item has been spotted in MIN_RATIO frames, keep currently
    MIN_RATIO = 0.7

    def __init__(self, cnt):
        self._cnt = cnt
        self._stayed = 0
        self._moved = 0

    def keep_item(self):
        ratio = self._stayed / (self._stayed + self._moved)
        if self._stayed > SuspiciousItem.MIN_STEPS or ratio > SuspiciousItem.MIN_RATIO:
            return True
        return False

    def get_contour(self):
        return self._cnt

    def update_item_status(self, stay):
        if stay:
            self._stayed += 1
        else:
            self._moved += 1


def main():
    session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    suspicious_items = []

    for i in range(len(session_images) - 1):
        im1 = cv2.imread(session_images[i])
        im2 = cv2.imread(session_images[i+1])

        # Call diff method
        diff = image_processing.DIFF_METHODS[DIFF_METHOD](im1, im2)
        cnts, diff = image_processing.get_contours(diff)

        # Add the new contours to the list of suspicious items
        suspicious_items += [SuspiciousItem(cnt) for cnt in cnts]

        # check which contours stayed from last time
        new_items = []
        for item in suspicious_items:
            similarity = image_processing.contour_stayed(im1, im2, item.get_contour())
            item.update_item_status(similarity > SIMILARITY_THRESH)
            if item.keep_item():
                new_items.append(item)
        suspicious_items = new_items

        cv2.imwrite("demos/demo" + str(i) + ".jpg", diff)
        cv2.imshow("Difference ", diff)
        cv2.waitKey(0)

    # output the final differences
    output = cv2.imread(session_images[0])
    output = image_processing.draw_rect_contours(output, [item.get_contour() for item in suspicious_items])
    cv2.imwrite("demos/final.jpg", output)
    cv2.imshow("Output", output)
    cv2.waitKey(0)



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