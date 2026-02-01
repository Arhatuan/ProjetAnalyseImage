class Parameters():
    """Contains parameters (defined by arguments on program's execution)"""

    evaluatedImages_filePath: str
    """Path to the file containing the list of images names to be evaluated"""

    imageCollection_directoryPath: str
    """Path to the directory containing all the image to be evaluated"""

    groundTruth_filePath: str
    """Path to the file containing the ground truth for the images to be evaluated"""

    evaluation_types: list[str]
    """The list of evaluations to be performed on the regression prediction (in order)"""

    regression_algorithm: str
    """The algorithm used for the regression prediction"""

    print_regression_details: bool
    """Show regression predictions"""
    
    def __init__(self, evaluatedImages_path: str, imageCollec_path: str, 
                 groundTruth_path: str, evaluation_types: list[str], solution_algo: str, print_regression_details: bool):
        
        self.evaluatedImages_filePath = evaluatedImages_path
        self.imageCollection_directoryPath = imageCollec_path
        self.groundTruth_filePath = groundTruth_path
        self.evaluation_types = evaluation_types
        self.regression_algorithm = solution_algo
        self.print_regression_details = print_regression_details