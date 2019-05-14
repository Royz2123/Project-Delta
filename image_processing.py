from skimage.measure import compare_ssim
import imutils
import cv2
import numpy as np

MIN_CNT_SIZE = 30
DIFFERENCE_THRESHOLD = 70
BACK_SUB = cv2.bgsegm.createBackgroundSubtractorLSBP()
BACK_SUB = cv2.createBackgroundSubtractorMOG2()
# BACK_SUB = cv2.bgsegm.createBackgroundSubtractorMOG()

EDGE_THICKNESS = 6

# Diff methods get 2 images as input, and output the diff matrix


def diff_method1(im1, im2):
    edges1 = cv2.Canny(im1, 100, 200)
    edges2 = cv2.Canny(im2, 100, 200)

    kernel = np.ones((EDGE_THICKNESS, EDGE_THICKNESS), np.uint8)
    edges1 = cv2.dilate(edges1, kernel)
    edges2 = cv2.dilate(edges2, kernel)

    diff = np.bitwise_and(~edges1, edges2)

    # clean noises
    kernel = np.ones((EDGE_THICKNESS - 1, EDGE_THICKNESS - 1), np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)

    cv2.imshow("Test", diff)
    cv2.waitKey(0)

    diff[diff > 0] = 1
    return diff


def diff_method2(im1, im2):
    diff = cv2.absdiff(im1, im2)
    diff = cv2.threshold(diff, DIFFERENCE_THRESHOLD, 255, cv2.THRESH_BINARY_INV)[1]
    diff = 255 - cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    diff[diff > 0] = 1
    return diff


def diff_method3(im1, im2):
    im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    im2 = cv2.equalizeHist(im2)
    im2 = cv2.GaussianBlur(im2, (5, 5), 0)
    fgmask = BACK_SUB.apply(im2)
    cv2.imshow("Difference ", fgmask)
    cv2.waitKey(0)
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
    cv2.waitKey(0)


def update_changes(mask, history, diff):
    # diff erode and dialate
    kernel = np.ones((4, 4), np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel)

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

    # create mask based on history
    new_mask = history.copy()
    new_mask[new_mask > 0] = 1
    new_mask[new_mask <= 0] = 0

    display_binary_im(new_mask)
    return new_mask, history

def draw_changes(img, mask):
    img[mask > 0] = [0, 0, 255]
    return img

def combine_masks(mask1, mask2):
    return np.bitwise_or(mask1, mask2)

def reliable_baseline(diff, percent=np.inf):
    height, width = diff.shape
    return np.sum(diff) < percent * (height * width)