import cv2
import os

from interface import Coordinates
from interface import CoordinatesVector
from interface import carCounter


def create_coordinates(x, y):
    c = Coordinates()
    c.x = x
    c.y = y
    return c


def test_call_vista_core():
    # Call the carCounter run function
    projectFolder = "C:\workspace\\vista\project\ctdot_test"
    videoFileLoc = os.path.join(projectFolder,
                                "videos",
                                "Standard_SCU3JD_2014-10-21_0845.012.mp4")
    imgFolder = os.path.join(projectFolder, "images", "")
    print os.path.abspath(imgFolder)
    databaseFileLoc = os.path.join(projectFolder, "car_count_db")
    video = cv2.VideoCapture(videoFileLoc)

    # Find OpenCV version and read the FPS
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    fpsVideo = video.get(cv2.cv.CV_CAP_PROP_FPS)  # assumes version openCV V2.
    print ("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}"
           .format(fpsVideo))
    video.release()

    bufferSize = 30                       # int
    minObjectSizeDay = 5000                 # int
    minObjectSizeNight = 10                  # int
    skip = 3                                # int
    learningTime = 240                        # int
    fileName = videoFileLoc                            # char length 100
    saveImgTo = imgFolder                           # char length 200
    dataBase = databaseFileLoc                            # char length 200

    fps = fpsVideo                                 # int
    expectedDist = 20                         # int
    horizontalBandwidth = 50                  # int
    online = True                              # bool

    # modified to pass overlays as an array  of Coordinate structs
    # which in turn is defined in VISTA
    # conversion into a form that is required by carCounter will happen in
    # run function

    # Defining overlays
    # Originally ppt and ppt2 were cv::Point*
    pptList = [create_coordinates(0, 0),
               create_coordinates(0, 480),
               create_coordinates(320, 480),
               create_coordinates(240, 0)]
    ppt = CoordinatesVector(pptList)
    ppt2List = [create_coordinates(230, 0),
                create_coordinates(720, 400),
                create_coordinates(720, 400),
                create_coordinates(720, 0)]
    ppt2 = CoordinatesVector(ppt2List)

    # originally npt and npt2 were int*
    npt = 4
    npt2 = 4

    useMOG2 = True                             # bool
    nmixtures = 5                           # int
    backgroundratio = 0.6                      # double
    detectShadows = True                        # bool
    showLastCar = True                         # bool
    boundBoxesOn = True                        # bool
    predictionOn = True                        # bool
    latestPathsOn = True                       # bool
    displayTransitLedger = True                # bool
    displayFocusRegions = True                 # bool
    showPathofId = -1                        # int
    displayType = 2                          # int

    # modified to pass a array of size N x 2 with coordinate
    # values defining the extents of the start and end region in the same order
    # conversion into a form that is required by carCounter will happen in
    # run function
    # Originall startRegion and endRegion were cv::vector<cv::Point>
    startRegionList = [create_coordinates(300, 250),
                       create_coordinates(600, 250),
                       create_coordinates(600, 300),
                       create_coordinates(300, 300)]
    startRegion = CoordinatesVector(startRegionList)
    endRegionList = [create_coordinates(300, 325),
                     create_coordinates(600, 325),
                     create_coordinates(600, 375),
                     create_coordinates(300, 375)]
    endRegion = CoordinatesVector(endRegionList)

    # Create carCounter obj
    cc = carCounter(5, True)
    cc.run(bufferSize, minObjectSizeDay, minObjectSizeNight, skip,
           learningTime,
           fileName, saveImgTo, dataBase,
           fps, expectedDist, horizontalBandwidth, online,
           ppt, ppt2,           # npt, npt2,
           useMOG2, nmixtures, backgroundratio,
           detectShadows, showLastCar, boundBoxesOn, predictionOn,
           latestPathsOn, displayTransitLedger, displayFocusRegions,
           showPathofId, displayType,
           startRegion, endRegion)

if __name__ == "__main__":
    test_call_vista_core()
