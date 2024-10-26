# rates_data_processing.py

class MovingAverageCalculator:
    def __init__(self, rates, nb_days_interval):
        """
        Initializes the instance with rate data and the interval for the moving average.
        :param rates: List of dictionaries with “date” and “value” keys
        :param nb_days_interval: Number of days for moving average interval
        """
        self.rates = rates
        self.nb_days_interval = nb_days_interval
    
    def compute_moving_average(self):
        """
         
        Calculates the moving average for rate data over the specified interval.
        :return: List of dictionaries with “date” and “value” keys representing moving averages.
        

        """
        averages = []  # List for storing moving averages
        s = 0  # Cumulative sum for current interval

        for i in range(len(self.rates)):
            rate = self.rates[i]
            s += rate["Close"]
            
            # Moving average calculation
            if i >= self.nb_days_interval:
                # Subtract the value that has been taken out of the interval
                s -= self.rates[i - self.nb_days_interval]["Close"]
                # Calculation of the average over the entire interval
                a = s / self.nb_days_interval
            else:
                # Average calculation for first days with incomplete interval
                a = s / (i + 1)
            
            # Add calculated average with associated date
            averages.append({"Date": rate["Date"], "Close": a})

        return averages