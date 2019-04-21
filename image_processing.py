from skimage.measure import compare_ssim
import imutils
import cv2


# Diff methods get 2 images as input, and output the diff matrix

def diff_method1(im1, im2):
    # convert the images to grayscale
    grayA = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    # print("SSIM: {}".format(score))

    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    return thresh


def diff_method2(im1, im2):
    return cv2.absdiff(im1, im2)


DIFF_METHODS = [
    diff_method1,
    diff_method2
]