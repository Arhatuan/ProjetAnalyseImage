from ..classes.ResultsToEvaluate import ResultsToEvaluate

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
            sum_value += (float(results[i].totalMonetaryValue_predicted) - float(results[i].totalMonetaryValue_groundTruth))**2
        sum_nbCoins /= len(results)
        sum_value /= len(results)
        return (sum_nbCoins, sum_value)


