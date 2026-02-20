import numpy as np
from numpy import ndarray
import cv2 as cv

def get_total_monetary_value(img: ndarray, circles: ndarray) -> float:

    template_action_on_each_circle(img, circles, showImageWithCircle=True)

    return 0


def get_zoomed_coin(img: ndarray, coinCenterX: float, coinCenterY: float, radius: float, k: float = 1.5) -> ndarray:
    """Get a squared-size zoomed image, centered on a coin.

    Args:
        img (ndarray): the original image containing the coin
        coinCenterX (float): the X center of the coin
        coinCenterY (float): the Y center of the coin
        radius (float): the radius of the circle, from its center
        k (float, optional): coefficient in regard to the radius. It's the size of the zoomed image, around the coin center. Defaults to 1.5.

    Returns:
        zoomed_coin (ndarray): the zoomed image centered on the coin
    """
    centerPoint = (coinCenterX, coinCenterY)

    xMin = max(0, int(centerPoint[0]) - int(k * radius)) 
    xMax = min(int(centerPoint[0]) + int(k * radius), img.shape[1] - 1)
    yMin = max(0, int(centerPoint[1]) - int(k * radius))
    yMax = min(int(centerPoint[1]) + int(k * radius), img.shape[0] - 1)

    zoomed_coin = img[yMin:yMax, xMin:xMax]
    return zoomed_coin

def get_only_coin_interior(img: ndarray, coinCenterX: float, coinCenterY: float, radius: float) -> ndarray:
    """Gets the image of only the coin (precisely, the interior of the circle describing the coin)

    Args:
        img (ndarray): the original image
        coinCenterX (float): the X center of the circle
        coinCenterY (float): the Y center of the circle
        radius (float): the circle's radius

    Returns:
        image_coin (ndarray): the image of only the coin (inside the circle describing it)
    """
    # Circular mask
    Y, X = np.ogrid[:img.shape[0], :img.shape[1]]
    mask = ((Y - coinCenterY)**2 + (X - coinCenterX)**2) <= radius**2

    # Apply the mask
    img_coin = np.copy(img)
    img_coin[np.invert(mask)] = 0

    img_coin = get_zoomed_coin(img_coin, coinCenterX, coinCenterY, radius, 1)

    return img_coin

def template_action_on_each_circle(img: ndarray, circles: ndarray, showImageWithCircle: bool = False):
    """Example on how to use the "circles" data.

    Args:
        img (ndarray): the original image
        circles (ndarray): circles found in the image
        showImageWithCircle (bool, optional): option to show the zoomed-in coins (with the circle drawn on it). Defaults to False.
    """
    # Exemple on how to use the 'circles' ndarray
    #   each line of 'circles' contains : xCenter, yCenter and radius of a circle

    for data in circles[0,:]:
        xCenter, yCenter, radius = data
        
        if not showImageWithCircle:
            zoomed_coin = get_zoomed_coin(img, xCenter, yCenter, radius, k=1.5)
        else:
            img_copy = np.copy(img)
            cv.circle(img_copy, (int(xCenter), int(yCenter)), int(radius), (255,0,0), 3) # draw the circle
            zoomed_coin = get_zoomed_coin(img_copy, xCenter, yCenter, radius, k=1.5)
            cv.imshow("Zoomed-in coin", zoomed_coin)
            cv.waitKey(0)
    






