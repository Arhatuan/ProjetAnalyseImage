import json

class FileParser():
    """Class with file reading and text parsing methods"""

    def file_reading(file_path: str) -> str:
        """Read a file, return its content

        Args:
            file_path (str): path to the file to read

        Raises:
            FileNotFoundError: the file doesn't exist
            ValueError: the file is empty

        Returns:
            str: the content of the file
        """
        try:
            with open(file_path) as file:
                text = file.read()
        except:
            raise FileNotFoundError(f"The file {file_path} doesn't exist.")
        
        if text.strip() == "":
            raise ValueError(f"The file '{file_path}' is empty.")
        
        return text

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
        
    