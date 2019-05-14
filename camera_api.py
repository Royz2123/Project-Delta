from arlo import Arlo
import cv2

arlo = Arlo("royzohar25@gmail.com", "1Qazwsxdcv")

# Get the list of devices and filter on device type to only get the camera.
# This will return an array which includes all of the camera's associated metadata.
cameras = arlo.GetDevices('camera')

basestations = cameras

print("Connected to Camera successfully")

# This method requests the snapshot for the given url and writes the image data to the location specified.
# In this case, to the current directory as a file named "snapshot.jpg"
# Note: Snapshots are in .jpg format.
def get_snapshot():
    # Tells the Arlo basestation to trigger a snapshot on the given camera.
    # This snapshot is not instantaneous, so this method waits for the response and returns the url
    # for the snapshot, which is stored on the Amazon AWS servers.

    while True:
        snapshot_url = arlo.TriggerFullFrameSnapshot(basestations[0], cameras[0])
        if snapshot_url is not None:
            break

    arlo.DownloadSnapshot(snapshot_url, 'temp.jpg')
    img = cv2.imread('temp.jpg')
    img = cv2.resize(img, (1000, 500))
    return img