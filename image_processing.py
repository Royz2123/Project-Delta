from skimage.measure import compare_ssim
import imutils
import cv2
import numpy as np

MIN_CNT_SIZE = 50

# Diff methods get 2 images as input, and output the diff matrix

def diff_method1(im1, im2):
    # convert the images to grayscale
    grayA = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    return diff


def diff_method2(im1, im2):
    return cv2.absdiff(im1, im2)


def draw_rect_contours(img, cnts):
    for c in cnts:
        # compute the bounding box of the contour and then draw the
        # bounding box on both input images to represent where the two
        # images differ
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return img


def get_contours(diff):
    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    final_cnts = [cnt for cnt in cnts if len(cnt) >= MIN_CNT_SIZE]
    draw_rect_contours(diff, final_cnts)

    return final_cnts, diff


# Compares two images regarding a certain contour
def mse(im1, im2, normalization):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    im1 = im1.astype("float") / float(255)
    im2 = im2.astype("float") / float(255)
    err = np.sum((im1 - im2) ** 2) / float(normalization)

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def contour_stayed(im1, im2, cnt):
    height, width, depth = im1.shape

    masks = []
    for img in [im1, im2]:
        mask = np.zeros((height, width), np.uint8)
        cv2.drawContours(mask, [cnt], 0, 1, 3)
        masked = cv2.bitwise_and(img, img, mask=mask)

        #cv2.imshow("masked", img)
        #cv2.waitKey(0)
        #cv2.imshow("masked", masked)
        #cv2.waitKey(0)

        masks.append(masked)

    similarity = mse(masks[0], masks[1], len(cnt))
    return similarity


DIFF_METHODS = [
    diff_method1,
    diff_method2
]