import types
import cv2 as cv
from .classes.Parameters import Parameters
from .tools.DataExtractor import DataExtractor
from .classes.ImageData import ImageData
from .classes.ResultsToEvaluate import ResultsToEvaluate
from .regression.RegressionAlgorithm1 import RegressionAlgorithm1
from .evaluation.evaluation import Evaluation

# The list of possible regression algorithms to apply
regressionAlgorithm = types.SimpleNamespace()
regressionAlgorithm.REGRESSION_ALGORITHM_1 = "regression_algorithm_1"
regressionAlgorithm.REGRESSION_ALGORITHM_2 = "regression_algorithm_2"

# The list of possible evaluations to apply
evaluations = types.SimpleNamespace()
evaluations.MAE = "mae"
evaluations.MSE = "mse"

class Manager():
    """Manage the parameters, the data extraction, the regression prediction and the evaluation"""

    def general_manager(parameters: Parameters):
        """Gets the image data, send them to the regression process to get results, and finally do the evaluation

        Args:
            parameters (Parameters): the parameters from the command line
        """
        
        # Data extraction
        img_data = DataExtractor.get_data_for_regression_and_evaluation(
            parameters.evaluatedImages_filePath,
            parameters.imageCollection_directoryPath,
            parameters.groundTruth_filePath,
        )

        # Regression process
        regression_results = Manager._manage_regression(img_data, parameters.regression_algorithm)

        # Print details
        if parameters.print_regression_details:
            Manager._print_details(regression_results)

        # Evaluation
        Manager._manage_evaluation(regression_results, parameters.evaluation_types)
    
    def _manage_regression(image_data: list[ImageData], regressionAlgo: str) -> list[ResultsToEvaluate]:
        """Apply a regression algorithm on each image, and return results that can be immediately evaluated

        Args:
            image_data (list[ImageData]): the data for each image we try to regress and evaluate
            regressionAlgo (str): the regression algorithm to use

        Returns:
            resultsForEvaluation (list[ResultsToEvaluate]): the results that can be immediately send for the evaluation
        """
        results = []

        for data in image_data:
            
            img = cv.imread(data.image_path) 
            if img is None:
                raise Exception(f"The file '{data.name}' couldn't be read as an image.")

            match regressionAlgo:
                case regressionAlgorithm.REGRESSION_ALGORITHM_1:
                    (nbCoins_predict, totalValue_predict) = RegressionAlgorithm1.get_nbCoins_and_totalMonetaryValue(img)
                case regressionAlgorithm.REGRESSION_ALGORITHM_2:
                    raise Exception("Regression algorithm n°2 not implemented")
                case _:
                    (nbCoins_predict, totalValue_predict) = RegressionAlgorithm1.get_nbCoins_and_totalMonetaryValue(img)

            img_result = ResultsToEvaluate(
                name = data.name,
                nbCoins_prediction = nbCoins_predict,
                nbCoins_groundTruth = data.nbCoins_groundTruth,
                totalValue_prediction = totalValue_predict,
                totalValue_groundTruth = data.totalValue_groundTruth
            )
            results.append(img_result)

        return results

    def _manage_evaluation(results: list[ResultsToEvaluate], evaluations_list: list[str]):
        """Evaluate some results from regression prediction. The evaluations is done in the order of the list of evaluations.

        Args:
            results (list[ResultsToEvaluate]): the results to evaluate
            evaluations_list (list[str]): the list of evaluations to do, in that order
        """

        for evaluation in evaluations_list:
            match evaluation:
                case evaluations.MAE:
                    (mae_nbCoins, mae_value) = Evaluation.MAE(results)
                    print("MAE number of coins = {:.3f}".format(mae_nbCoins))
                    print("MAE monetary value = {:.3f}".format(mae_value))
                    print()
                case evaluations.MSE:
                    (mse_nbCoins, mse_value) = Evaluation.MSE(results)
                    print("MSE number of coins = {:.3f}".format(mse_nbCoins))
                    print("MSE monetary value = {:.3f}".format(mse_value))
                    print()

    def _print_details(results: list[ResultsToEvaluate]):
        """Print the predictions and ground truths

        Args:
            results (list[ResultsToEvaluate]): the results to showcase
        """
        # 1) Get the maximum lengths of the parameters to print
        len_name, len_nbC_pred, len_nbC_GT, len_value_pred, len_value_GT = (0,0,0,0,0)
        for data in results:
            len_name = max(len_name, len(data.image_name))
            len_nbC_pred = max(len_nbC_pred, len(str(data.nbCoins_predicted)))
            len_nbC_GT = max(len_nbC_GT, len(str(data.nbCoins_groundTruth)))
            len_value_pred = max(len_value_pred, len(str(data.totalMonetaryValue_predicted)))
            len_value_GT = max(len_value_GT, len(str(data.totalMonetaryValue_groundTruth)))

        # 2) Get the strings to print
        len_name += 3
        len_nbC_pred = max(len_nbC_pred, len("Prediction"))
        len_nbC_GT = max(len_nbC_GT, len("Ground Truth"))
        len_value_pred = max(len_value_pred, len("Prediction"))
        len_value_GT = max(len_value_GT, len("Ground Truth"))
        space_in_between = 7

        # Line 1
        constructedLines = " "*len_name 
        constructedLines += ("{:^"+str(len_nbC_pred+len_nbC_GT+3)+"}").format("Number of coins")
        constructedLines += " "*space_in_between
        constructedLines += ("{:^"+str(len_value_pred+len_value_GT+3)+"}").format("Monetary value")
        constructedLines += "\n"

        # Line 2
        constructedLines += " "*len_name
        constructedLines += ("{:^"+str(len_nbC_pred+len_nbC_GT+3)+"}").format("Prediction / Ground Truth")
        constructedLines += " "*space_in_between
        constructedLines += ("{:^"+str(len_value_pred+len_value_GT+3)+"}").format("Prediction / Ground Truth")
        constructedLines += "\n"

        # One line per image data
        for data in results:
            constructedLines += ("{:<"+str(len_name)+"}").format(f"{data.image_name} :")

            constructedLines += ("{:>"+str(len_nbC_pred)+"}").format(data.nbCoins_predicted)
            constructedLines += " / "
            constructedLines += ("{:<"+str(len_nbC_GT)+"}").format(data.nbCoins_groundTruth)

            constructedLines += ("{:^"+str(space_in_between)+"}").format("|")

            constructedLines += ("{:>"+str(len_value_pred)+"}").format(data.totalMonetaryValue_predicted)
            constructedLines += " / "
            constructedLines += str(data.totalMonetaryValue_groundTruth)
            
            constructedLines += "\n"
        
        print(constructedLines)

