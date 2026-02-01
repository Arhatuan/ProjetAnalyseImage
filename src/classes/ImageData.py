class ImageData():
    """A structure for the image data : its name, the image itself, 
    and its ground truth concerning the number of coins and the total monetary value."""

    name: str
    """The image's file name"""

    image_path: str
    """The image itself"""

    nbCoins_groundTruth: int
    """The number of coins in the image, according to the ground truth"""

    totalValue_groundTruth: float
    """The total monetary value of the coins in the image, according to the ground truth"""

    def __init__(self, name: str, img_path: str, 
                 nbCoins_groundTruth: int, totalValue_groundTruth: float):
        self.name = name
        self.image_path = img_path
        self.nbCoins_groundTruth = nbCoins_groundTruth
        self.totalValue_groundTruth = totalValue_groundTruth

