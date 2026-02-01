from ..classes.ImageData import ImageData
from .FileParser import FileParser
from pathlib import Path
import os

class DataExtractor():
    """General class for data extraction (image list, image data, ground truth...)"""

    def get_data_for_regression_and_evaluation(filePath_evaluatedImages: str, 
            directoryPath_imageCollection: str, filePath_groundTruth: str) -> list[ImageData]:
        """Extract all the necessary data for the regression and evaluation work

        Args:
            filePath_evaluatedImages (str): path to the file containing the list of image names
            directoryPath_imageCollection (str): path to the directory containing all the images
            filePath_groundTruth (str): path to the file containing the ground truth for the images to evaluate

        Returns:
            list[ImageData]: the list of data per image
        """
        list_imgs_to_evaluate = DataExtractor._get_list_of_images_to_evaluate(filePath_evaluatedImages)
        data_groundTruth = DataExtractor._get_ground_truth(filePath_groundTruth, list_imgs_to_evaluate)
        absolutePaths_images = DataExtractor._get_images_absolute_paths(directoryPath_imageCollection, list_imgs_to_evaluate)

        return DataExtractor._create_image_data(data_groundTruth, absolutePaths_images)


    def _get_list_of_images_to_evaluate(filePath_imageList: str) -> list[str]:
        """Extracts the list of image names from a file (describing an image database)

        Args:
            filePath_imageList (str): file containing a list of image names

        Raises:
            Exception: file doesn't exist, or file is empty

        Returns:
            list[str]: a list of image names for evaluation
        """
        try:
            text = FileParser.file_reading(filePath_imageList)
        except Exception as e:
            raise Exception(str(e) + "\n(this file is supposed to contain the list of images for regression and evaluation)")

        imagesNames = text.split() # Each line has an image name
        imagesNames = list(set(imagesNames)) # To delete duplicates

        return imagesNames

    def _get_ground_truth(filePath_groundTruth: str, list_images: list[str]) -> dict[str, tuple[int, float]]:
        """Extracts the ground truth from a file. Only retains images from the given list.

        Args:
            filePath_groundTruth (str): path to the ground truth file
            list_images (list[str]): the list of images we work with

        Raises:
            Exception: the file doesn't exist, or is empty
            ValueError: the file doesn't have ground truth data for some images from the list

        Returns:
            data_groundTruth (dict[str, tuple[int, float]]): key = image name, value = tuple[nb coins, total monetary value]
        """
        try:
            text = FileParser.file_reading(filePath_groundTruth)
        except Exception as e:
            raise Exception(str(e) + "\n(this file is supposed to contain the ground truth for the images)")
        
        data_groundTruth = FileParser.parse_ground_truth(text)

        # We check that each image name exist in this dictionary
        for image_name in list_images:
            if (not image_name in data_groundTruth.keys()):
                raise ValueError(f"The ground truth file doesn't have data for the '{image_name}' file.")

        # We delete useless entries (image that aren't used for regression and evaluation)
        final_data_groundTruth = { k:v for (k,v) in data_groundTruth.items() if k in list_images}

        return final_data_groundTruth
    
    def _get_images_absolute_paths(directoryPath_imageCollection: str, list_images: list[str]) -> dict[str, str]:
        """Get the list of valid image paths (the images will be read when necessary ; we just check they exist)

        Args:
            directoryPath_imageCollection (str): path to the directory containing the images
            list_images (list[str]): the list of image names

        Raises:
            FileNotFoundError: the directory containing the images doesn't exist
            FileNotFoundError: an necessary image couldn't be found in the directory

        Returns:
            absolutePaths (dict[str, str]): key = image name, value = absolute path
        """
        if not Path(directoryPath_imageCollection).is_dir():
            raise FileNotFoundError(f"The directory '{directoryPath_imageCollection}' doesn't exist.")
        
        dict_image_paths = {}
        for image_name in list_images:
            img_path = os.path.join(directoryPath_imageCollection, image_name)
            if Path(img_path).is_file():
                dict_image_paths[image_name] = img_path
            else:
                raise FileNotFoundError(f"The image '{image_name}' couldn't be found at '{img_path}'.")
        
        return dict_image_paths

    def _create_image_data(data_groundTruth: dict[str, tuple[int, float]], absolutePaths_images: dict[str, str]) -> list[ImageData]:
        """Create an ImageData for each image, based on the ground truth and the absolute paths previously extracted

        Args:
            data_groundTruth (dict[str, tuple[int, float]]): data from the ground truth file
            absolutePaths_images (dict[str, str]): absolute paths of the images

        Raises:
            ValueError: (development error) the two parameters have different keys lists

        Returns:
            imageData_list (list[ImageData]): the list of ImageData 
        """
        if set(data_groundTruth.keys()) != set(absolutePaths_images.keys()):
            raise ValueError("Error in the program : the ground truths and the image paths don't have the same keys")
        
        list_imageData = []

        for image_name in data_groundTruth.keys():
            (nbCoins, totalMonetaryValue) = data_groundTruth[image_name]
            imgPath = absolutePaths_images[image_name]

            object_imageData = ImageData(name = image_name,
                                         img_path = imgPath,
                                         nbCoins_groundTruth = nbCoins,
                                         totalValue_groundTruth = totalMonetaryValue)
            
            list_imageData.append(object_imageData)

        return list_imageData

