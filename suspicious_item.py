import random

MOVEMENT_THRESH = 0.7

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

