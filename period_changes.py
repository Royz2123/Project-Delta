import numpy as np


class Period:

    def __init__(self,start_at=100):
        self.width = 500
        self.height = 1000
        self.diff_sum = np.zeros((self.width,self.height))
        self.length = 0
        self.pre = None
        self.start_at = start_at

    def add_diff(self, diff):
        if self.pre is None:
            self.pre = diff.copy()
        self.diff_sum += np.absolute(diff.copy() - self.pre)
        self.pre = diff.copy()
        self.length += 1

    def get_period_changes(self,threshold=0.1):
        if self.length <= self.start_at:
            return np.ones((self.width,self.height))
        return np.where(self.diff_sum.copy()/(self.length-1) < threshold, np.ones((self.width,self.height)), np.zeros((self.width,self.height)))
