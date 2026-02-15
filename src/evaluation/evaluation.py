from ..classes.ResultsToEvaluate import ResultsToEvaluate
import math

class Evaluation():

    def MAE(results: list[ResultsToEvaluate]) -> tuple[float, float]:
        """Compute the Mean Absolute Error (MAE), 
        the absolute difference between each prediction and ground truth,
        for both the number of coins and the monetary value (separately)

        Args:
            results (list[ResultsToEvaluate]): the results to evaluate

        Returns:
            MAE_nbCoins,MAE_value (tuple[float, float]): MAE for number of coins, MAE for monetary value 
        """
        sum_nbCoins = 0
        sum_value = 0
        for i in range(len(results)):
            sum_nbCoins += abs(float(results[i].nbCoins_predicted) - float(results[i].nbCoins_groundTruth))
            if str(results[i].totalMonetaryValue_groundTruth) == "nan":
                continue # ignore the invalid ground truth
            sum_value += abs(float(results[i].totalMonetaryValue_predicted) - float(results[i].totalMonetaryValue_groundTruth))
        sum_nbCoins /= len(results)
        sum_value /= len(results)
        return (sum_nbCoins, sum_value)
    
    def MSE(results: list[ResultsToEvaluate]) -> tuple[float, float]:
        """Compute the Mean Squared Error (MSE),
        the squared difference between each prediction and ground truth,
        for both the number of coins and the monetary value (separately)

        Args:
            results (list[ResultsToEvaluate]): the results to evaluate

        Returns:
            MSE_nbCoins,MSE_value (tuple[float, float]): MSE for number of coins, MSE for monetary value 
        """
        sum_nbCoins = 0
        sum_value = 0
        for i in range(len(results)):
            sum_nbCoins += (float(results[i].nbCoins_predicted) - float(results[i].nbCoins_groundTruth))**2
            if str(results[i].totalMonetaryValue_groundTruth) == "nan":
                continue # ignore the invalid ground truth
            sum_value += (float(results[i].totalMonetaryValue_predicted) - float(results[i].totalMonetaryValue_groundTruth))**2
        sum_nbCoins /= len(results)
        sum_value /= len(results)
        return (sum_nbCoins, sum_value)

    def get_number_perfect_nb_coins_prediction(results: list[ResultsToEvaluate]) -> tuple[int, int, int]:
        """Gets the number of perfect predictions (and other statistics) concerning the number of coins in the images.

        Args:
            results (list[ResultsToEvaluate]): the list of results to evaluate (prediction + ground truth for multiple images)

        Returns:
            (nbPerfectPredictions,_nbNearPerfectPredictions,_nbNotGoodPredictions) (tuple[int, int, int]): 
                the number of perfect predictions, of predictions with difference of 1 or 2 from ground truth, and predictions with more than 2 of difference
        """
        nbPerfectPredictions = 0
        nbNearPerfectPredictions = 0
        nbNotGoodPredictions = 0

        for result in results:
            difference = abs(result.nbCoins_predicted - result.nbCoins_groundTruth)
            if difference == 0:
                nbPerfectPredictions += 1
            elif difference <= 2:
                nbNearPerfectPredictions += 1
            else:
                nbNotGoodPredictions += 1

        return (nbPerfectPredictions, nbNearPerfectPredictions, nbNotGoodPredictions)
    
    def get_string_proportions_nb_coins_predictions(results: list[ResultsToEvaluate]) -> str:
        """String containing the proportions of good and bad predictions for the number of coins

        Args:
            results (list[ResultsToEvaluate]): the results to evaluate

        Returns:
            str: the string describing the proportions
        """
        (nbPerfectPredictions, nbNearPerfectPredictions, nbNotGoodPredictions) = Evaluation.get_number_perfect_nb_coins_prediction(results)

        lines = "• Results proportions\n"
        lines += "\tPerfect prediction | Difference of 1 or 2 | Difference > 2\n"

        lines += ("\t{:^"+str(len("Perfect prediction"))+".2%}").format(nbPerfectPredictions / len(results))
        lines += (" | {:^"+str(len("Difference of 1 or 2"))+".2%}").format(nbNearPerfectPredictions / len(results))
        lines += (" | {:^"+str(len("Difference > 2"))+".2%}").format(nbNotGoodPredictions / len(results))

        return lines

    def get_strings_MAE(results: list[ResultsToEvaluate]) -> tuple[str, str]:
        """Strings containing the MAE evaluation concerning the results to evaluate

        Args:
            results (list[ResultsToEvaluate]): results to evaluate

        Returns:
            string_MAE_nbCoins,_string_MAE_monetaryValue (tuple[str, str]): one string for the MAE about the number of coins, another string for the MAE about the monetary value
        """
        (global_nbCoins_MAE, global_monetaryValue_MAE) = Evaluation.MAE(results)

        # Only not perfect nb coins predictions
        listNotPerfectNbCoinsPrediction = [result for result in results if result.nbCoins_groundTruth != result.nbCoins_predicted]
        (notPerfect_nbCoins_MAE, _) = Evaluation.MAE(listNotPerfectNbCoinsPrediction)

        # Only perfect nb coins predictions
        listPerfectNbCoinsPrediction = [result for result in results if result.nbCoins_groundTruth == result.nbCoins_predicted]
        (_, perfectNbCoins_monetaryValue_MAE) = Evaluation.MAE(listPerfectNbCoinsPrediction)

        # For number of coins
        linesNbCoins = "• MAE\n"
        linesNbCoins += "\tGlobal | Only not perfect predictions\n"
        linesNbCoins += ("\t{:^"+str(len("Global"))+".2f}").format(global_nbCoins_MAE)
        linesNbCoins += (" | {:^"+str(len("Only not perfect predictions"))+".2f}").format(notPerfect_nbCoins_MAE)

        # For monetary value
        linesMonetaryValue = "• MAE\n"
        linesMonetaryValue += "\tGlobal | Only perfect number of coins predictions\n"
        linesMonetaryValue += ("\t{:^"+str(len("Global"))+".2f}").format(global_monetaryValue_MAE)
        linesMonetaryValue += (" | {:^"+str(len("Only perfect number of coins predictions"))+".2f}").format(perfectNbCoins_monetaryValue_MAE)

        return (linesNbCoins, linesMonetaryValue)

    def get_strings_MSE(results: list[ResultsToEvaluate]) -> tuple[str, str]:
        """Strings containing the MSE evaluation concerning the results to evaluate

        Args:
            results (list[ResultsToEvaluate]): the results to evaluate

        Returns:
            string_MSE_nbCoins,_string_MSE_monetaryValue (tuple[str, str]): one string for the MSE about the number of coins, another string for the MSE about the monetary value
        """
        # All predictions
        (global_nbCoins_MSE, global_monetaryValue_MSE) = Evaluation.MSE(results)

        # Only not perfect nb coins predictions
        listNotPerfectNbCoinsPrediction = [result for result in results if result.nbCoins_groundTruth != result.nbCoins_predicted]
        (notPerfect_nbCoins_MSE, _) = Evaluation.MSE(listNotPerfectNbCoinsPrediction)

        # Only perfect nb coins predictions
        listPerfectNbCoinsPrediction = [result for result in results if result.nbCoins_groundTruth == result.nbCoins_predicted]
        (_, perfectNbCoins_monetaryValue_MSE) = Evaluation.MSE(listPerfectNbCoinsPrediction)

        # For number of coins
        linesNbCoins = "• MSE\n"
        linesNbCoins += "\tGlobal | Only not perfect predictions\n"
        linesNbCoins += ("\t{:^"+str(len("Global"))+".2f}").format(global_nbCoins_MSE)
        linesNbCoins += (" | {:^"+str(len("Only not perfect predictions"))+".2f}").format(notPerfect_nbCoins_MSE)

        # For monetary value
        linesMonetaryValue = "• MSE\n"
        linesMonetaryValue += "\tGlobal | Only perfect number of coins predictions\n"
        linesMonetaryValue += ("\t{:^"+str(len("Global"))+".2f}").format(global_monetaryValue_MSE)
        linesMonetaryValue += (" | {:^"+str(len("Only perfect number of coins predictions"))+".2f}").format(perfectNbCoins_monetaryValue_MSE)

        return (linesNbCoins, linesMonetaryValue)

