from enum import Enum

from skimage.feature import hog
from skimage.measure import compare_ssim
import imutils
import cv2
import numpy as np

IMAGE_SHOW_DELAY = 15

MIN_CNT_SIZE = 30
DIFFERENCE_THRESHOLD = 30
HOG_THRESHOLD = 3


LEARNING_RATE = 0.02
STAY_FACTOR = 7
INF = 100000

# BACK_SUB = cv2.createBackgroundSubtractorMOG2()
# BACK_SUB = cv2.bgsegm.createBackgroundSubtractorGMG(4, 0.8)

BACK_SUB1 = cv2.bgsegm.createBackgroundSubtractorLSBP(minCount=1, LSBPthreshold=10, Tlower=10, Tupper=20)
BACK_SUB2 = cv2.bgsegm.createBackgroundSubtractorMOG(history=10000, nmixtures = 5, backgroundRatio = 0.6, noiseSigma = 0)
BACK_SUB3 = cv2.bgsegm.createBackgroundSubtractorGSOC(replaceRate=0.05, propagationRate=0.0001, alpha=0.05, beta=0.05)

EDGE_THICKNESS = 6

# Diff methods get 2 images as input, and output the diff matrix


def diff_edges(im1, im2):
    edges1 = cv2.Canny(im1, 100, 200)
    edges2 = cv2.Canny(im2, 100, 200)

    kernel = np.ones((EDGE_THICKNESS, EDGE_THICKNESS), np.uint8)
    edges1 = cv2.dilate(edges1, kernel)
    edges2 = cv2.dilate(edges2, kernel)

    diff = np.bitwise_and(~edges1, edges2)

    # clean noises
    kernel = np.ones((EDGE_THICKNESS - 1, EDGE_THICKNESS - 1), np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)

    # cv2.imshow("Test", diff)

    diff[diff > 0] = 1
    return diff


def diff_sub(im1, im2):
    diff = cv2.absdiff(im1, im2)
    # diff = cv2.equalizeHist(diff)
    diff = cv2.threshold(diff, DIFFERENCE_THRESHOLD, 255, cv2.THRESH_BINARY_INV)[1]
    diff = 255 - cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    diff[diff > 0] = 1
    return diff


def diff_background_sub_1(im1, im2):
    return back_sub(im1, im2, BACK_SUB1)


def diff_background_sub_2(im1, im2):
    return back_sub(im1, im2, BACK_SUB2)


def diff_background_sub_3(im1, im2):
    return back_sub(im1, im2, BACK_SUB3)

def diff_hog(im1, im2):
    original_shape = im2.shape
    im1 = cv2.resize(im1, (1010, 510))
    im2 = cv2.resize(im2, (1010, 510))

    hog1 = hog(im1, orientations=9, pixels_per_cell=(10, 10), feature_vector=False,
               cells_per_block=(2, 2), multichannel=True)
    hog2 = hog(im2, orientations=9, pixels_per_cell=(10, 10), feature_vector=False,
               cells_per_block=(2, 2), multichannel=True)

    diff = cv2.absdiff(hog2, hog1)
    diff = np.sum(diff, (2,3,4))

    diff[diff < HOG_THRESHOLD] = 0
    diff = cv2.resize(diff, (original_shape[1], original_shape[0]))

    kernel = np.ones((3, 3), np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel, iterations=2)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel, iterations=2)

    # cv2.imshow("Test", diff)
    # cv2.waitKey(0)
    diff[diff <= HOG_THRESHOLD] = 0
    diff[diff > HOG_THRESHOLD] = 1
    return diff

def diff_ssim(im1, im2):
    # convert the images to grayscale
    grayA = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")

    kernel = np.ones((3, 3), np.uint8)
    # diff = cv2.dilate(diff, kernel, iterations=1)
    # diff = cv2.erode(diff, kernel, iterations=1)

    diff = cv2.threshold(diff, DIFFERENCE_THRESHOLD, 255, cv2.THRESH_BINARY_INV)[1]
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel, iterations=6)


    diff[diff > 0] = 1

    return diff

def intersectMethods(im1, im2):
    methods = [DiffMethods.BACKGROUND_SUB_2, DiffMethods.HOG, DiffMethods.BACKGROUND_SUB_3]
    # weights = [0.2, 0.7, 0.4, 0.4]
    weights = [0.7,0.3,0.3]
    total_diff = np.array(methods[0](im1, im2)) * weights[0]
    #cv2.imshow("basic changes " + get_method_name(methods[0]), 255 * total_diff.astype(float))
    i = 1
    for method in methods[1:]:
        diff = np.array(method(im1, im2))
        #cv2.imshow("basic changes " + get_method_name(method), 255 * diff.astype(float))
        #print(method)
        total_diff += diff * weights[i]
        i += 1
        # cv2.imshow("intersection " + str(i), 255 * total_diff.astype(float))
    total_diff[total_diff >= 1] = 1
    total_diff[total_diff < 1] = 0
    return total_diff

def back_sub(im1, im2, back_sub):
    im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    # im2 = cv2.equalizeHist(im2)
    im2 = cv2.GaussianBlur(im2, (5, 5), 0)
    fgmask = back_sub.apply(im2, learningRate=LEARNING_RATE)

    kernel = np.ones((EDGE_THICKNESS, EDGE_THICKNESS), np.uint8)
    fgmask = cv2.dilate(fgmask, kernel)

    # cv2.imshow("Difference ", fgmask)
    # k = cv2.waitKey(300) & 0xff

    fgmask[fgmask > 0] = 1
    return fgmask


def draw_rect_contours(img, cnts):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    except:
        pass

    for c in cnts:
        # compute the bounding box of the contour and then draw the
        # bounding box on both input images to represent where the two
        # images differ
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return img


def get_contours(diff):
    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    # thresh = cv2.threshold(diff, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    final_cnts = [cnt for cnt in cnts if len(cnt) >= MIN_CNT_SIZE]
    return final_cnts


# Compares two images regarding a certain contour
def mse(im1, im2, normalization):
    im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

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


def create_changes_dbs(im):
    height, width, depth = im.shape
    return np.zeros((height, width), np.uint8), np.zeros((height, width), np.int32)


def display_binary_im(bin_im):
    bin_im = bin_im.astype(np.uint8)
    bin_im[bin_im > 0] = 255
    cv2.imshow("Difference ", bin_im)
    k = cv2.waitKey(IMAGE_SHOW_DELAY) & 0xff


def update_changes(mask, history, diff):
    # diff erode and dialate
    #kernel = np.ones((2, 2), np.uint8)
    #diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)
    #diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel)

    """
    # get changes
    stayed_changes = np.bitwise_and(mask, diff)
    moved_changes = mask - diff

    # binarize
    stayed_changes[stayed_changes > 0] = 1
    moved_changes[stayed_changes > 0] = 1
    moved_changes[moved_changes < 0] = 0
    
    # add to history
    history += stayed_changes
    history -= moved_changes
    """

    # add to history
    history[diff == 0] -= 2
    history[np.bitwise_and(diff == 1, history < 0)] = 0
    history[diff == 1] += 1

    # check for persistent changes
    history[history >= STAY_FACTOR] = INF

    # create mask based on history
    new_mask = history.copy()
    new_mask[new_mask > 0] = 1
    new_mask[new_mask <= 0] = 0

    display_binary_im(new_mask)
    return new_mask, history


def draw_changes(img, mask):
    contours, _	= cv2.findContours(mask.copy().astype(np.uint8),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE )
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
    return img

def combine_masks(mask1, mask2):
    return np.bitwise_or(mask1, mask2)

def reliable_baseline(diff, percent=np.inf):
    height, width = diff.shape
    return np.sum(diff) < percent * (height * width)

class DiffMethods(Enum):
    EDGES = diff_edges
    BASIC_SUB = diff_sub
    BACKGROUND_SUB_1 = diff_background_sub_1
    BACKGROUND_SUB_2 = diff_background_sub_2
    BACKGROUND_SUB_3 = diff_background_sub_3
    HOG = diff_hog
    SSIM = diff_ssim
    INTERSECT = intersectMethods
def get_method_name(method):
    return str(method).split(" ")[1]

