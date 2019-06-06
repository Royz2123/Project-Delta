import numpy as np
import datetime

class Period:

    def __init__(self,start_at=100):
        self.width = 3#500
        self.height = 3#1000
        self.diff_sum = np.zeros((self.width,self.height))
        self.length = 0
        self.pre = None
        self.start_at = start_at
        self.all = np.zeros((0,self.width,self.height))
        self.t = np.zeros(0)

    def add_diff(self, diff, name):
        if self.pre is None:
            self.pre = diff.copy()
        self.diff_sum += np.absolute(diff.copy() - self.pre)
        self.pre = diff.copy()
        self.length += 1

        self.all = np.append(self.all, [diff], axis=0)
        self.t = np.append(self.t, self.get_img_time(name))

    def get_period_changes(self,threshold=0.1,enable=True):
        if self.length <= self.start_at or not enable:
            return np.ones((self.width,self.height))
        return np.where(self.diff_sum.copy()/(self.length-1) < threshold, np.ones((self.width,self.height)), np.zeros((self.width,self.height)))

    def day_changes(self):
        t = self.t[-1]
        r = np.zeros((self.width, self.height), dtype=bool)
        result = np.ones((self.width, self.height), dtype=bool)
        for i in range(self.length-1,-1,-1):
            if self.t[i] <= t - 24 * 60 * 60 - 15 * 60:
                t = t - 24 * 60 * 60
                result = np.logical_and(result,r)
                r = np.zeros((self.width, self.height), dtype=bool)
            if t - 24*60*60 - 15*60 < self.t[i] < t - 24*60*60 + 15*60:
                r = np.logical_or(r,self.all[-1, :, :] == self.all[i, :, :])
                if i == 0:
                    t = t - 24 * 60 * 60
                    result = np.logical_and(result, r)
                    r = np.zeros((self.width, self.height), dtype=bool)
        return result


    def get_img_time(self, img_name):
        return datetime.datetime.strptime(img_name,
                                          "%Y_%m_%d_%H_%M_%S.jpg").timestamp()

if __name__=='__main__':
    a = np.array([[0, 1, 1],
                  [1, 1, 1],
                  [0, 1, 1]])
    a_name = "2019_05_28_09_10_25.jpg"

    b = np.array([[1, 1, 1],
                  [1, 0, 1],
                  [1, 0, 0]])
    b_name = "2019_05_28_09_05_25.jpg"

    c2 = np.array([[1, 0, 0],
                  [0, 1, 1],
                  [1, 1, 1]])
    c2_name = "2019_05_27_09_20_25.jpg"

    c = np.array([[0, 0, 0],
                  [1, 1, 1],
                  [0, 0, 0]])
    c_name = "2019_05_27_08_59_25.jpg"

    d = np.array([[0,0,0],
                  [1,0,0],
                  [0,1,1]])
    d_name = "2019_05_26_09_10_25.jpg"

    p = Period()
    p.add_diff(d,d_name)
    p.add_diff(c, c_name)
    p.add_diff(c2, c2_name)
    p.add_diff(b, b_name)
    p.add_diff(a, a_name)
    print(p.day_changes())