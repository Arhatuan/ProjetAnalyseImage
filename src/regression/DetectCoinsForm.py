import numpy as np
from numpy import ndarray
import cv2 as cv

SHORTEST_SIDE_LENGTH = 500

def get_circles(img: ndarray) -> tuple[ndarray, int]:
        """Get the circles around the coins in the image, as they are automatically detected

        Args:
            img (ndarray): the image with coins

        Returns:
            circles,_nb_circles (tuple[ndarray, int]): the N circles are contained in a (1,N,3) matrix 
                    (each line contains 3 data for a circle : center X and Y coordinates, and radius)
        """

        # Resize the image to 500px on the shortest side (and equivalent resizing on the other side)
        resized = _resize_lowest_side_of_image(img, SHORTEST_SIDE_LENGTH)

        # Pre-treatment : gray-scale + median blur
        gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)
        grayBlurred = cv.medianBlur(gray, 7)

        # Choose the Canny's high threshold
        canny_high_threshold = _get_canny_high_threshold(grayBlurred, 1)
        
        # Choose the circle's minimum and maximum radiuses
        #   values based on personal observations on some images 
        minRadius = int(50 * 0.66)
        maxRadius = int(177 * 1.33)

        circles = cv.HoughCircles(
            grayBlurred, 
            method = cv.HOUGH_GRADIENT, 
            dp = 1.2, 
            minDist = 2*minRadius,
            param1 = canny_high_threshold+20,
            param2 = 50,
            minRadius = minRadius-30,  
            maxRadius = maxRadius
        )
        
        # Circles are resized according to the image original sizes
        circles = _resize_circles_back_to_original_size(circles, gray.shape[1], img.shape[1])

        nbCircles = circles.shape[1] if circles is not None else 0
        return (circles, nbCircles)


def _get_canny_high_threshold(img: ndarray, canny_threshold_method: int = 1) -> int:
    """Apply a method to compute a candidate for a high threshold in a canny filter

    Args:
        img (ndarray): the image we want to threshold
        canny_threshold_method (int, optional): 2 options (1 = Otsu's method, 2 = median method). Defaults to 1.

    Returns:
        high_threshold (int): the high threshold proposed
    """
    match canny_threshold_method:
        case 1: high_thresh, thresh_im = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU) # Otsu's method
        case 2: high_thresh = min(255, 1.33 * np.median(img)) # 1.33 * median value
        case _: pass
    return int(high_thresh)
    
def _resize_lowest_side_of_image(img: ndarray, new_lowest_size: int) -> ndarray:
    """Resize an image where the shortest side gets the value given as a parameter.

    Args:
        img (ndarray): the image to resize
        new_lowest_size (int): the new length of the shortest side

    Returns:
        resized_img (ndarray): a new resized image
    """
    shortest_side = 0 if img.shape[0] <= img.shape[1] else 1 # 0 = height, 1 = width
    
    # Resize the lowest side to the value 'new_lowest_size'
    resize_factor = new_lowest_size / img.shape[shortest_side]
    new_width = int(img.shape[0] * resize_factor)
    new_height = int(img.shape[1] * resize_factor)
    
    resized_img = cv.resize(img, dsize = (new_height, new_width))
    return resized_img

def _resize_circles_back_to_original_size(circles: ndarray, resized_width: int, original_width: int) -> ndarray:
    """Interpolate the circles's data after going back to the original image sizes

    Args:
        circles (ndarray): data for N circles, in a matrix of shape (1,N,3), each line containing data for a circle's center X and Y coordinates, and its radius
        resized_width (int): the width of the resized image
        original_width (int): the width of the original image (before the resizing)

    Returns:
        circles_resized (ndarray): same data than the 'circles' parameter, but with updated values to account for resizing back to the original image sizes
    """
    resize_back_factor = original_width / resized_width

    if circles is not None:
        for i in circles[0, :]:
            i[0] *= resize_back_factor # center X coordinate
            i[1] *= resize_back_factor # center Y coordinate
            i[2] *= resize_back_factor # radius 

    return circles

def _show_image_with_circles(img: ndarray, circles: ndarray):
    """Show an image with circles printed on it

    Args:
        img (ndarray): the image
        circles (ndarray): the N circles, in a matrix of shape (1,N,3), with each line containg a circle's data (its center's X and Y coordinates, and its radius)
    """
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv.circle(img, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv.circle(img, center, radius, (255, 0, 255), 3)
    
    cv.imshow("detected circles", img)
    cv.waitKey(0)

