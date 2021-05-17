from statistics import mean


class SMA:
    """Simple moving average"""

    def __init__(self, period):
        self.period = int(period)
        self.last_prices = []
        self.averages = []

    def append_value(self, item):
        """
        Append new value for calculate

        Calculate by formula:
        SMA(i) = (SUM(CLOSE[-N:])) / N
        """
        self.last_prices.append(item)
        if len(self.last_prices) > self.period:
            self.last_prices.pop(0)

        self.averages.append(mean(self.last_prices))

    def __len__(self):
        return len(self.averages)

    def __getitem__(self, index):
        return self.averages[index]
