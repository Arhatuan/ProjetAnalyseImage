import cv2 as cv
from .DetectCoinsForm import get_circles
from .PredictMonetaryValue import get_total_monetary_value

SHORTEST_SIDE_LENGTH = 500


class RegressionAlgorithm1():

    def get_nbCoins_and_totalMonetaryValue(img_path: str) -> tuple[int, float]:
        """Gets the number of coins, and the monetary value of an image containing coins

        Args:
            img_path (str): the path to the image containg coins

        Raises:
            Exception: couldn't read the image

        Returns:
            nbCoins,_totalMonetaryValue (tuple[int, float]): the number of coins, and the total monetary value
        """

        img = cv.imread(img_path) 
        if img is None:
            raise Exception(f"The file '{img_path}' couldn't be read as an image.")
        
        (circles, nbCircles) = get_circles(img)

        monetaryValue = get_total_monetary_value(img, circles)
        
        return (nbCircles, monetaryValue)


    