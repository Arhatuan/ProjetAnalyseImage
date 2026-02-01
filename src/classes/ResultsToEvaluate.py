class ResultsToEvaluate():
    """Structure containing the results to evaluate : the prediction compared to the ground truth"""

    image_name: str
    """The name of the image"""

    nbCoins_predicted: int
    """The prediction of the number of coins"""

    nbCoins_groundTruth: int
    """The ground truth of the number of coins"""

    totalMonetaryValue_predicted: float
    """The prediction of the total monetary value"""

    totalMonetaryValue_groundTruth: float
    """The ground truth of the total monetary value"""

    def __init__(self, name: str, nbCoins_prediction: int, nbCoins_groundTruth: int,
                 totalValue_prediction: float, totalValue_groundTruth: float):
        self.image_name = name
        self.nbCoins_predicted = nbCoins_prediction
        self.nbCoins_groundTruth = nbCoins_groundTruth
        self.totalMonetaryValue_predicted = totalValue_prediction
        self.totalMonetaryValue_groundTruth = totalValue_groundTruth
