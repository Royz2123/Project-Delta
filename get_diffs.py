import cv2
import os

import image_processing



DIFF_METHOD = 0

def main():
    session_path = "sessions/" + max(os.listdir("sessions/")) + "/"
    session_images = [session_path + path for path in sorted(os.listdir(session_path))]

    for i in range(len(session_images) - 1):
        im1 = cv2.imread(session_images[i])
        im2 = cv2.imread(session_images[i+1])

        # Call diff method
        diff = image_processing.DIFF_METHODS[DIFF_METHOD](im1, im2)

        cv2.imwrite("demos/demo" + str(i) + ".jpg", diff)
        cv2.imshow("Difference ", diff)
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