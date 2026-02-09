import json
import pandas
import os

class FileParser():
    """Class with file reading and text parsing methods"""

    def file_list_images_reading(file_path: str) -> list[str]:
        """Read a file containing a list of images file names, return its content

        Args:
            file_path (str): path to the file to read

        Raises:
            FileNotFoundError: the file doesn't exist
            ValueError: the file is empty

        Returns:
            list[str]: the list of the images file names
        """
        try:
            with open(file_path) as file:
                text = file.read()
        except:
            raise FileNotFoundError(f"The file {file_path} doesn't exist.")
        
        if text.strip() == "":
            raise ValueError(f"The file '{file_path}' is empty.")
        
        list_image_names = text.split()
        final_list = []
        for name in list_image_names:
            final_list.append( os.path.join(*name.split("/")) )
        
        return final_list

    def parse_ground_truth(groundTruth_text: str) -> dict[str, tuple[int, float]]:
        """Parse a ground truth text into a dictionary

        Args:
            groundTruth_text (str): the text of a ground truth file (expected to be a JSON)

        Raises:
            ValueError: the ground truth text is not in the predicted JSON format

        Returns:
            dict[str, tuple[int, float]]: the parsed data from the ground truth file
        """
        try:
            dict_groundTruth = json.loads(groundTruth_text)
            # At this point, this is a dict (key = image names) of dicts (value = dict with 2 keys 'nbCoins' and 'totalValue')
            # We have to convert this to a dict with tuple values
            final_dict = {k: (v['nbCoins'], v['totalValue']) for (k,v) in dict_groundTruth.items()}
        except:
            raise ValueError(f"The content of the ground truth file couldn't be parsed in an ground truth object.")

        return final_dict
        
    
    def excel_file_reading_and_parsing_ground_truth(file_path: str) -> dict[str, tuple[int, float]]:
        """Read a excel file wontaining the ground truth, and parse its content

        Args:
            file_path (str): the path to excel file

        Raises:
            FileNotFoundError: the file doesn't exist, or isn't in the expected format for parsing

        Returns:
            dict[str, tuple[int, float]]: key = image file name, value = tuple( number of coins, monetary value)
        """
        try:
            text = pandas.read_excel(file_path, 
                                    names = ["img_name", "nb_coins", "monetary_value", "group"],
                                    dtype = {"img_name": str, "nb_coins": int, "monetary_value": float, "group": str},
                                    skiprows=2,
                                    )

            dict_text = text.to_dict(orient='list')
        except:
            raise FileNotFoundError(f"the file {file_path} doesn't exist, or isn't in the expected format.")

        final_dict = {}
        for i in range(len(dict_text["img_name"])):
            fileName = os.path.join(dict_text["group"][i], dict_text["img_name"][i])
            nbCoins = dict_text["nb_coins"][i]
            monetaryValue = dict_text["monetary_value"][i]
            final_dict[fileName] = (nbCoins, monetaryValue)

        return final_dict
    