import numpy as np

def is_night_mode(img):
    return np.allclose(img[:,:,0],img[:,:,1]) and np.allclose(img[:,:,1],img[:,:,2])
