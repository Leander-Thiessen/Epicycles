import numpy as np
import matplotlib.pyplot as plt
import PIL
import cv2
from numpy.random import default_rng
np.random.seed(41)


def rotate(l, n):
    return np.append(l[n:],l[:n])

def import_points_from_png(filename,width,height,M=0,plot=False,shift=0):
    img = cv2.imread(filename)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    ret, thresh = cv2.threshold(img_gray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    X,Y = np.array([]),np.array([])
    L = len(contours)
    print(L)
    for i in range(1,2):
        contour = np.array(contours[i])

        #contours = np.array(contours[2]) 
        x, y = contour[:, :, 0], -contour[:, :, 1]
        X = np.append(X,x)
        Y = np.append(Y,y)

    print(f"maximum number of points available: {len(X)}")
    points_x = X#[:,0]
    points_y = Y#[:,0]

    x_mean = int(np.mean(points_x))
    y_mean = int(np.mean(points_y))

    points_x -= x_mean
    points_y -= y_mean
    
    #x_scale = 1.1 #int(np.max(points_x)-np.min(points_x)/width)
    scale = (np.max(points_y)-np.min(points_y))/height + 0.1
    #print(scale)

    points_x = points_x / scale
    points_y = points_y / scale

    points_x = rotate(points_x,shift)
    points_y = rotate(points_y,shift)

    if M != 0 or M>len(points_x):
        rng = default_rng()
        index_choice = np.sort(rng.choice(len(points_x), size=M, replace=False))

        points_x = points_x[index_choice]
        points_y = points_y[index_choice]

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(points_x, points_y,".",markersize=1)
        plt.show()

    if len(points_x) % 2 == 0:
        return np.array(list(zip(points_x,points_y)))
    else:
        return np.array(list(zip(points_x[:-1],points_y[:-1])))



#points = import_points_from_png("pictures/catnew.png",1280, 720,plot=True)

# dist = []
# for i in range(len(points)-1):
#     d = np.sqrt(abs(points[i+1][0]-points[i][0])**2 + abs(points[i+1][1]-points[i][1])**2)
#     print(d)
#     dist.append(d)
# print(len(points))
# print(i:=np.argmax(dist))
# print(dist[i])