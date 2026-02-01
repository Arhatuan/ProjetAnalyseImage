import argparse
import os
from pathlib import Path
from src import Manager
from src.classes.Parameters import Parameters



DEFAULT_FILE_IMGS_TO_EVALUATE_PATH = os.path.join(Path(__file__).parent, 'data', 'default_imgs_to_evaluate.txt')
"""Path to the default file containing the list of images' names to evaluate"""

DEFAULT_DIRECTORY_IMG_COLLECTION_PATH = os.path.join(Path(__file__).parent, 'data', 'img_database')
"""Path to the default directory containing all the images to evaluate 
(can contain other images, but they won't be considered)"""

DEFAULT_FILE_GROUND_TRUTH_PATH = os.path.join(Path(__file__).parent, 'data', 'default_ground_truth.txt')
"""Path to the file containing the ground truth for each image to evaluate
(can contain ground truth for other images, but they won't be considered)"""



def parse_arguments() -> Parameters:
    """Parse the arguments from the command line,
    and return the parameters to use for the project.

    Returns:
        Parameters: an object containing the necessary parameters for the project
    """

    parser = argparse.ArgumentParser(prog="Project Image Analysis",
                description="Make a regression prediction based on given images")

    # Arguments for files to process.
    #   There are default files and directory, but the user can present different ones.
    parser.add_argument("-f", "--fileToEvaluate",
                        default = None,
                        metavar = 'file_imagesToEvaluate',
                        help = "file name that contains a list of images' names to evaluate (relative path)")
    parser.add_argument("-d", "--dirImages",
                        default = None,
                        metavar = 'directory_images',
                        help = "directory containing all the necessary images to evaluate (relative path)")
    parser.add_argument("-g", "--fileGroundTruth",
                        default = None,
                        metavar = 'file_groundTruth',
                        help = "file containing the ground truth for the images to evaluate (relative path)")
    
    # Optional additional arguments
    parser.add_argument('-e', '--evaluationType',
                        choices = ['MAE', 'MSE'],
                        nargs = '*',
                        default = ['MSE'],
                        type = str.upper,
                        help = 'option to choose the evaluation to apply (default : MSE)')
    
    parser.add_argument('-r', '--regressionAlgorithm',
                        choices = ['1', '2'],
                        default = '1',
                        help = 'option to choose the regression algorithm (default : 1)')
    
    parser.add_argument("-p", "--printDetails",
                        action="store_true",
                        help = "print details about the regression predictions and ground truth for each file (default: False)")
    
    args = parser.parse_args()


    # If the files and directory are the default ones, we have to check they exist
    #   -> test for the file containing the images' names to evaluate
    if (args.fileToEvaluate is None):
        args.fileToEvaluate = DEFAULT_FILE_IMGS_TO_EVALUATE_PATH
        if (not Path(DEFAULT_FILE_IMGS_TO_EVALUATE_PATH).is_file()):
            parser.error("\nThe default file containing a list of images' names to evaluate "
                        + "doesn't exist \n\t(file 'data/default_img_to_evaluate.txt')"
                        + "\nPlease give a substitute file with the option '-f'")
    #   -> test for the directory containing all the images
    if (args.dirImages is None):
        args.dirImages = DEFAULT_DIRECTORY_IMG_COLLECTION_PATH
        if (not Path(DEFAULT_DIRECTORY_IMG_COLLECTION_PATH).is_dir()):
            parser.error("\nThe default directory containing all the images to evaluate doesn't exist"
                        + "\n\t(directory 'data/img_database')"
                        + "\nPlease give a substitute directory with the option '-d'")
    #   -> test for the file containing the ground truth
    if (args.fileGroundTruth is None):
        args.fileGroundTruth = DEFAULT_FILE_GROUND_TRUTH_PATH
        if (not Path(DEFAULT_FILE_GROUND_TRUTH_PATH).is_file()):
            parser.error("\nThe default file containing the ground truth doesn't exist"
                        + "\n\t(file 'data/default_ground_truth.txt')"
                        + "\nPlease give a substitute file with the option '-g'")

    # Choice of the evaluation
    evaluationList = []
    for evaluationType in args.evaluationType:
        match evaluationType:
            case 'MAE': evaluationList.append(Manager.evaluations.MAE)
            case 'MSE': evaluationList.append(Manager.evaluations.MSE)
            case _: pass
    
    # Choice of the regression algorithm
    match args.regressionAlgorithm:
        case '1': regressionAlgo = Manager.regressionAlgorithm.REGRESSION_ALGORITHM_1
        case '2': regressionAlgo = Manager.regressionAlgorithm.REGRESSION_ALGORITHM_2
        case _: regressionAlgo = Manager.regressionAlgorithm.REGRESSION_ALGORITHM_1

    
    # Initialization of the parameters
    params = Parameters(evaluatedImages_path = args.fileToEvaluate,
                        imageCollec_path = args.dirImages,
                        groundTruth_path = args.fileGroundTruth,
                        evaluation_types = evaluationList,
                        solution_algo = regressionAlgo,
                        print_regression_details = args.printDetails)
    
    return params
    


if __name__ == "__main__":
    params = parse_arguments()

    try:
        Manager.Manager.general_manager(params)
    except Exception as e:
        print(f"Error : {e}")
