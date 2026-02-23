<<<<<<< HEAD
from enum import Enum

class CoinType(Enum):
    EURO = 1
    COPPER = 2
    GOLD = 3

class CoinValue(Enum):
    EURO_2 = 2.0
    EURO_1 = 1.0
    CENT_50 = 0.5
    CENT_20 = 0.2
    CENT_10 = 0.1
    CENT_5 = 0.05
    CENT_2 = 0.02
    CENT_1 = 0.01

real_coins_diameters = {
    CoinValue.EURO_2: 25.75,
    CoinValue.EURO_1: 23.25,
    CoinValue.CENT_50: 24.25,
    CoinValue.CENT_20: 22.25,
    CoinValue.CENT_10: 19.75,
    CoinValue.CENT_5: 21.25,
    CoinValue.CENT_2: 18.75,
    CoinValue.CENT_1: 16.25
}

possible_values_by_type = {
    CoinType.COPPER: [CoinValue.CENT_1, CoinValue.CENT_2, CoinValue.CENT_5],
    CoinType.GOLD: [CoinValue.CENT_10, CoinValue.CENT_20, CoinValue.CENT_50],
    CoinType.EURO: [CoinValue.EURO_1, CoinValue.EURO_2]
}

class CoinData():
    xCenter: float
    yCenter: float
    radius: float
    coinType: CoinType | None
    value: CoinValue | None

    def __init__(self, xCenter: float, yCenter: float, radius: float):
        self.xCenter = xCenter
        self.yCenter = yCenter
        self.radius = radius
        self.coinType = None
        self.value = None

    def __str__(self):
        return ("• Coin : ({:.1f}, {:.1f}) -> radius : {:.1f} \t|| type : {}, \t value : {}"
                .format(self.xCenter, self.yCenter, self.radius, self.coinType, self.value))