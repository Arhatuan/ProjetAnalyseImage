import numpy as np
from numpy import ndarray
import cv2 as cv
import skimage

from ..classes.CoinData import CoinData, CoinType, CoinValue, real_coins_diameters, possible_values_by_type

def get_total_monetary_value(img: ndarray, circles: ndarray) -> float:
    """Get the total monetary value of the coins in an image, knowing where the coins are.

    Args:
        img (ndarray): the original image containing coins
        circles (ndarray): the N circles are contained in an (1,N,3) matrix, with values for each circle = (xCenter, yCenter, radius)

    Returns:
        total_monetary_value (float): the total monetaru value of the coins in the image
    """

    coinData_list = init_CoinData_struct(circles)
    update_radiuses(img, coinData_list)

    update_coins_types(img, coinData_list, showImageAndDetails=False)
    update_coins_values(coinData_list, img, showImageAndDetails=False)

    total_monetary_value = 0
    for coinData in coinData_list:
        total_monetary_value += coinData.value.value

    return np.round(total_monetary_value, 2)


def get_zoomed_coin(img: ndarray, coinCenterX: float, coinCenterY: float, radius: float, k: float = 1.5) -> ndarray:
    """Get a squared-size zoomed image, centered on a coin.

    Args:
        img (ndarray): the original image containing the coin
        coinCenterX (float): the X center of the coin
        coinCenterY (float): the Y center of the coin
        radius (float): the radius of the circle, from its center
        k (float, optional): coefficient in regard to the radius. It's the size of the zoomed image, around the coin center. Defaults to 1.5.

    Returns:
        zoomed_coin (ndarray): the zoomed image centered on the coin
    """
    centerPoint = (coinCenterX, coinCenterY)

    xMin = max(0, int(centerPoint[0]) - int(k * radius)) 
    xMax = min(int(centerPoint[0]) + int(k * radius), img.shape[1] - 1)
    yMin = max(0, int(centerPoint[1]) - int(k * radius))
    yMax = min(int(centerPoint[1]) + int(k * radius), img.shape[0] - 1)

    zoomed_coin = img[yMin:yMax, xMin:xMax]
    return zoomed_coin

def get_only_coin_interior(img: ndarray, coinCenterX: float, coinCenterY: float, radius: float) -> ndarray:
    """Gets the image of only the coin (precisely, the interior of the circle describing the coin)

    Args:
        img (ndarray): the original image
        coinCenterX (float): the X center of the circle
        coinCenterY (float): the Y center of the circle
        radius (float): the circle's radius

    Returns:
        image_coin (ndarray): the image of only the coin (inside the circle describing it)
    """
    # Circular mask
    Y, X = np.ogrid[:img.shape[0], :img.shape[1]]
    mask = ((Y - coinCenterY)**2 + (X - coinCenterX)**2) <= radius**2

    # Apply the mask
    img_coin = np.copy(img)
    img_coin[np.invert(mask)] = 0

    img_coin = get_zoomed_coin(img_coin, coinCenterX, coinCenterY, radius, 1)

    return img_coin

def template_action_on_each_circle(img: ndarray, circles: ndarray, showImageWithCircle: bool = False):
    """Example on how to use the "circles" data.

    Args:
        img (ndarray): the original image
        circles (ndarray): circles found in the image
        showImageWithCircle (bool, optional): option to show the zoomed-in coins (with the circle drawn on it). Defaults to False.
    """
    # Exemple on how to use the 'circles' ndarray
    #   each line of 'circles' contains : xCenter, yCenter and radius of a circle

    for data in circles[0,:]:
        xCenter, yCenter, radius = data
        
        if not showImageWithCircle:
            zoomed_coin = get_zoomed_coin(img, xCenter, yCenter, radius, k=1.5)
        else:
            img_copy = np.copy(img)
            cv.circle(img_copy, (int(xCenter), int(yCenter)), int(radius), (255,0,0), 3) # draw the circle
            zoomed_coin = get_zoomed_coin(img_copy, xCenter, yCenter, radius, k=1.5)
            cv.imshow("Zoomed-in coin", zoomed_coin)
            cv.waitKey(0)



def circular_mask(img: ndarray, centerX: int, centerY: int, radius: float) -> ndarray:
    """Get a circular mask of an image, based on a center point and a radius

    Args:
        img (ndarray): the image to apply a circular mask
        centerX (int): the x center of the circle
        centerY (int): the y center of the circle
        radius (float): the radius of the circle

    Returns:
        circularMask (ndarray): the circular mask of the image
    """
    Y, X = np.ogrid[:img.shape[0], :img.shape[1]]
    mask = ((Y - centerY)**2 + (X - centerX)**2) <= radius**2
    return mask

def get_internal_and_external_ring_masks(img: ndarray, centerX: int, centerY: int, radius: float) -> tuple[ndarray, ndarray]:
    """Return masks for the internal region, and the external ring of a coin.

    Args:
        img (ndarray): the image of the coin
        centerX (int): x center of the coin
        centerY (int): y center of the coin
        radius (float): radius of the coin, from its center

    Returns:
        internalMask,_externalRingMask (tuple[ndarray, ndarray]): the internal mask, and the external ring mask
    """
    internal_mask = circular_mask(img, centerX, centerY, radius * 0.6)
    partial_internal_mask = circular_mask(img, centerX, centerY, radius * 0.7)
    total_mask = circular_mask(img, centerX, centerY, radius * 0.85)
    external_ring_mask = total_mask ^ partial_internal_mask
    return (internal_mask, external_ring_mask)


def gray_world(img: ndarray) -> ndarray:
    """Apply the Gray World assumption on an image.

    Args:
        img (ndarray): the image to change

    Returns:
        ndarray: the image after applying the method
    """
    img = img.astype(np.float32)

    # Compute channel means
    mean_r = np.mean(img[:,:,2])
    mean_g = np.mean(img[:,:,1])
    mean_b = np.mean(img[:,:,0])

    mean_gray = (mean_r + mean_g + mean_b) / 3

    # Scaling factors
    scale_r = mean_gray / mean_r
    scale_g = mean_gray / mean_g
    scale_b = mean_gray / mean_b

    # Apply scaling
    img[:,:,2] *= scale_r
    img[:,:,1] *= scale_g
    img[:,:,0] *= scale_b

    # Clip values
    img = np.clip(img, 0, 255)

    return img.astype(np.uint8)

def normalize_hsv_rescaled(hsv_img: ndarray) -> ndarray:
    """Normalize an HSV image (goes to [-1;1] range), then rescale to [0;179] scale

    Args:
        hsv_img (ndarray): the HSV image to normalize

    Returns:
        ndarray: the final normalized and rescaled HSV image
    """
    hue_mean = np.mean(hsv_img[:,:,0])
    hue_std = np.std(hsv_img[:,:,0])
    saturation_mean = np.mean(hsv_img[:,:,1])
    saturation_std = np.std(hsv_img[:,:,1])
    value_mean = np.mean(hsv_img[:,:,2])
    value_std = np.std(hsv_img[:,:,2])

    # Normalize to [-1;1]
    normalized_hue = (hsv_img[:,:,0] - hue_mean) / hue_std
    normalized_saturation = (hsv_img[:,:,1] - saturation_mean) / saturation_std
    normalized_value = (hsv_img[:,:,2] - value_mean) / value_std

    # Rescale to [0;179] for hue, and [0;255] for saturation
    hue_rescale = (normalized_hue - normalized_hue.min()) / (normalized_hue.max() - normalized_hue.min())
    hue_rescale = (hue_rescale * 179).astype(np.uint8)

    saturation_rescale = (normalized_saturation - normalized_saturation.min()) / (normalized_saturation.max() - normalized_saturation.min())
    saturation_rescale = (saturation_rescale * 255).astype(np.uint8)

    value_rescale = (normalized_value - normalized_value.min()) / (normalized_value.max() - normalized_value.min())
    value_rescale = (value_rescale * 255).astype(np.uint8)

    value_hist_equalized = cv.equalizeHist(value_rescale)

    normalized_hsv = np.dstack((hue_rescale, saturation_rescale, value_hist_equalized))
    return normalized_hsv


def update_coins_types(img: ndarray, list_coinData: list[CoinData], showImageAndDetails: bool = False):
    """Choose a type for each coin : euro type (1€ or 2€), 
    gold type (50c, 20c or 10c) or copper type (5c, 2c or 1c).

    Args:
        img (ndarray): the original image
        list_coinData (list[CoinData]): list containing data for each coin. Will update the 'coinType' and 'value' attributes.
        showImageAndDetails (bool, optional): show images and details about each coin's choice of its type. Defaults to False.
    """
    hue_values = []

    # 1) Detect 1e and 2e coins, and gets the hue and saturation means sums
    for coinData in list_coinData:
        # 1.1) Get only the zoomed coin
        zoomed_coin = get_zoomed_coin(img, coinData.xCenter, coinData.yCenter, coinData.radius, k=1)
        new_xCenter, new_yCenter = (zoomed_coin.shape[0]//2, zoomed_coin.shape[0]//2)

        # 1.2) Get the masks (global, internal region and external ring)
        globalMask = circular_mask(zoomed_coin, new_xCenter, new_yCenter, coinData.radius)
        (internal_mask, external_ring_mask) = get_internal_and_external_ring_masks(zoomed_coin, new_xCenter, new_yCenter, coinData.radius)

        # 1.3) Compute the coin image in hsv color scale
        gw_coin = gray_world(zoomed_coin) 
        hsv_coin = cv.cvtColor(gw_coin, cv.COLOR_BGR2HSV)
        hsv_coin = normalize_hsv_rescaled(hsv_coin)

        # 1.4) Compute mean hue for coin's central region and external ring
        hInternal_data = hsv_coin[internal_mask][:,0]
        hInternal_mean = np.mean(hInternal_data)
        
        hExternal_data = hsv_coin[external_ring_mask][:,0]
        hExternal_mean = np.mean(hExternal_data)

        # 1.5) Decide if the coin is of euro type (1e or 2e) or of cents type
        if abs(hInternal_mean - hExternal_mean) > 10:
            # if euro, we can decide its value immediately, 
            #   based on the difference between the interior region and the external ring
            coinData.coinType = CoinType.EURO
            coinData.value = CoinValue.EURO_1 if hInternal_mean > hExternal_mean else CoinValue.EURO_2

            if showImageAndDetails:
                print("• Euro : ({:.1f}, {:.1f}) => {}€".format(hInternal_mean, hExternal_mean, coinData.value.value))
                cv.imshow("t", zoomed_coin); cv.waitKey(0)
        else:
            # cents are to be decided after getting the global hue and saturation from all the coins of type 'cents'
            hue_values.extend(hInternal_data) 

    # 2) Decide for the coins of type 'cents'

    # 2.1) Automatically choose a threshold value to separate cents coin of type 'copper' and 'golden'
    hist1, bin1 = np.histogram(hue_values, bins=180, range=(0,179))
    hist1 = strip_histogram_beyond_quartiles(hist1, 0.25, 0.75)
    threshold_hue = skimage.filters.threshold_otsu(hist=hist1)

    if showImageAndDetails:
        print("\t== threshold : {:.1f} ==".format(threshold_hue))
    
    # 2.2) Decide the type of cents
    list_coins_with_undecided_coinTypes = [coinD for coinD in list_coinData if coinD.coinType is None]
    for coinData in list_coins_with_undecided_coinTypes:
        # 2.2.1) Get only the zoomed coin
        zoomed_coin = get_zoomed_coin(img, coinData.xCenter, coinData.yCenter, coinData.radius, k=1)
        new_xCenter, new_yCenter = (zoomed_coin.shape[0]//2, zoomed_coin.shape[0]//2)

        # 2.2.2) Get the masks (global, internal region and external ring)
        globalMask = circular_mask(zoomed_coin, new_xCenter, new_yCenter, coinData.radius)
        (internal_mask, external_ring_mask) = get_internal_and_external_ring_masks(zoomed_coin, new_xCenter, new_yCenter, coinData.radius)

        # 2.2.3) Compute the coin image in hsv color scale
        gw_coin = gray_world(zoomed_coin) 
        hsv_coin = cv.cvtColor(gw_coin, cv.COLOR_BGR2HSV)
        hsv_coin = normalize_hsv_rescaled(hsv_coin)

        # 2.2.4) Compute mean hue for coin's central region and external ring
        hInternal_data = hsv_coin[internal_mask][:,0]
        hInternal_mean = np.mean(hInternal_data)

        hInternal_mean = get_weighted_mean_of_hue_by_saturation(hsv_coin, internal_mask)

        # 2.2.5) Decice if the cent coin is of 'copper' or 'gold' type
        if hInternal_mean < threshold_hue:
            coinData.coinType = CoinType.COPPER
        else:
            coinData.coinType = CoinType.GOLD

        if showImageAndDetails:
            print("• Cent : {:.1f} => {}".format(hInternal_mean, str.split(str(coinData.coinType), ".")[1]))
            cv.imshow("t", zoomed_coin); cv.waitKey(0)



def update_coins_values_voting_method(list_coinData: list[CoinData], img: ndarray = None, showImageAndDetails: bool = False):
    """Choose a value for each coin, using a voting method

    Args:
        list_coinData (list[CoinData]): list containing the coin's data. Will update the 'value' attribute of each coin. 
        img (ndarray, optional): the image, only if showing details. Defaults to None.
        showImageAndDetails (bool, optional): option to show the coin's image, with the value decided. Defaults to False.
    """
    # Global method (even for euros)
    for i in range(len(list_coinData)):
        coinData = list_coinData[i]
        rest_coinDatas = list_coinData[:i] + list_coinData[i+1:]
        firstCoin_values = possible_values_by_type[coinData.coinType]

        bestMatch = CoinValue.CENT_1 # default
        bestScore = float("inf")
        votes = []
        
        for coinData_compared in rest_coinDatas:
            
            ratio_basic = coinData.radius / coinData_compared.radius
            secondCoin_values = possible_values_by_type[coinData_compared.coinType]

            for value1 in firstCoin_values:
                for value2 in secondCoin_values:
                    ratio_theoretical = real_coins_diameters[value1] / real_coins_diameters[value2]
                    score = abs(ratio_theoretical - ratio_basic)
                    
                    if score < bestScore:
                        bestScore, bestMatch = score, value1
            
            votes.append(bestMatch)
        
        coinData.value = max(votes, key=votes.count)
        
        if showImageAndDetails and img is not None:
            print([v.value for v in votes])
            print(f"Final : {coinData.value}")
            zoomed_coin = get_zoomed_coin(img, coinData.xCenter, coinData.yCenter, coinData.radius, k=1)
            cv.imshow("t", zoomed_coin); cv.waitKey(0)


def update_coins_values(list_coinData: list[CoinData], img: ndarray = None, showImageAndDetails: bool = False):
    """Choose a value for each, if there are euros as a reference, or if there aren't any

    Args:
        list_coinData (list[CoinData]): list containing the coin's data. Will update the 'value' attribute of each coin. 
        img (ndarray, optional): the image, only if showing details. Defaults to None.
        showImageAndDetails (bool, optional): option to show the coin's image, with the value decided. Defaults to False.
    """
    names_copper_cents = [v for v in CoinValue if v.value < 0.1]
    names_golden_cents = [v for v in CoinValue if 0.1 <= v.value < 1] 

    list_eurosDatas = [dataCoin for dataCoin in list_coinData if dataCoin.coinType == CoinType.EURO]
    list_centsDatas = [dataCoin for dataCoin in list_coinData if dataCoin.coinType != CoinType.EURO]

    # 1) Compare to euros coins already detected
    if len(list_eurosDatas) > 0:

        for centsCoin in list_centsDatas:
            bestMatch = CoinValue.CENT_1 # default
            bestScore = float("inf")

            for euroCoin in list_eurosDatas:

                ratio_basic = centsCoin.radius / euroCoin.radius
                
                # get the list of possible 'cents' options, depending on its color
                possible_cents_names = names_copper_cents if centsCoin.coinType == CoinType.COPPER else names_golden_cents
                
                # compare to every possible 'cents' options
                for coinValue in possible_cents_names:
                    ratio_theoritical = real_coins_diameters[coinValue] / real_coins_diameters[euroCoin.value]
                    score = abs(ratio_theoritical - ratio_basic)

                    if score < bestScore:
                        bestScore, bestMatch = score, coinValue

            centsCoin.value = bestMatch
            
            if showImageAndDetails and img is not None:
                print(f"• Cent : {centsCoin.value.value}")
                zoomed_coin = get_zoomed_coin(img, centsCoin.xCenter, centsCoin.yCenter, centsCoin.radius, k=1)
                cv.imshow("t", zoomed_coin); cv.waitKey(0)

    # 2) If no euro coin : only cents
    else:
        update_coins_values_voting_method(list_coinData, img, showImageAndDetails)


def get_weighted_mean_of_hue_by_saturation(hsv_img: ndarray, mask: ndarray) -> float:
    """Gets the weighted mean of hue by saturation

    Args:
        hsv_img (ndarray): the HSV image
        mask (ndarray): the mask

    Returns:
        weighted_mean (float): the weighted mean of hue by saturation
    """
    weighted_mean = 0
    sumSaturation = 0
    for h,s,v in hsv_img[mask]:
        weighted_mean += float(h)*float(s)
        sumSaturation += float(s)
    weighted_hue = weighted_mean / sumSaturation
    return weighted_hue
 

def strip_histogram_beyond_quartiles(hist: ndarray, Q1: float = 0.1, Q2: float = 0.9) -> ndarray:
    """Strip indexes of an histogram (value = 0) such as only data between the quartiles Q1 and Q2 have positive values

    Args:
        hist (ndarray): the histogram to strip
        Q1 (float, optional): the first quartile (data before it goes to 0). Defaults to 0.1.
        Q2 (float, optional): the second quartile (data after it goes to 0). Defaults to 0.9.

    Returns:
        stripped_hist (ndarray): the stripped histogram
    """
    valueQ1 = np.sum(hist) * Q1
    valueQ2 = np.sum(hist) * Q2
    tempSum = 0
    argQ1, argQ2 = None, None
    for i in range(len(hist)):
        tempSum += hist[i]
        if not argQ1 and tempSum > valueQ1:
            argQ1 = max(i-1, 0)
        if not argQ2 and tempSum > valueQ2:
            argQ2 = i

    hist[:argQ1] = 0
    hist[argQ2:] = 0

    return hist

def init_CoinData_struct(circles: ndarray) -> list[CoinData]:
    """Initialize the structure containing the CoinData for each coin

    Args:
        circles (ndarray): the N circles's data in a (1,N,3) matrix, with values for each coin = (xCenter, yCenter, radius)

    Returns:
        list[CoinData]: the structure containing CoinData for each coin
    """
    coinData_list = []
    for data in circles[0,:]:
        xCenter, yCenter, radius = data
        coinData = CoinData(xCenter, yCenter, radius)
        coinData_list.append(coinData)
    return coinData_list


def _refine_radius_with_s_profile(list_coinData: list[CoinData], img_saturation: ndarray, n_angles=36, drop_ratio=0.5):
    """
    Raffine le rayon de chaque cercle via un profil radial sur le canal S.
    Pour chaque cercle :
      - On tire n_angles rayons depuis le centre vers l'extérieur
      - On cherche sur chaque rayon où S chute sous drop_ratio * S_centre
      - Le vrai rayon = médiane de ces points de chute
    """
    h, w    = img_saturation.shape
    angles  = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)

    for coinData in list_coinData:
        cx, cy, r = int(coinData.xCenter), int(coinData.yCenter), int(coinData.radius)
        s_centre  = img_saturation[min(cy, h-1), min(cx, w-1)]
        threshold = max(10.0, drop_ratio * s_centre)

        edge_radii = []
        for angle in angles:
            for ri in range(r, int(r * 0.5), -1):
                px = int(cx + ri * np.cos(angle))
                py = int(cy + ri * np.sin(angle))
                if 0 <= px < w and 0 <= py < h:
                    if img_saturation[py, px] > threshold:
                        edge_radii.append(ri)
                        break

        if len(edge_radii) > n_angles // 2:
            coinData.radius = int(np.median(edge_radii))



def update_radiuses(img: ndarray, list_coinData: list[CoinData]):
    """Change the radiuses of every coin data, based on the refine method

    Args:
        img (ndarray): the image containing coins
        list_coinData (list[CoinData]): the list of coin data. Will update the 'radius' attribute of each coin data.
    """
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img_saturation = img_hsv[:,:,1].astype(float) # saturation is 2nd channel
    _refine_radius_with_s_profile(list_coinData, img_saturation)
    
