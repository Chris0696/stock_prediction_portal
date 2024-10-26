import requests
import json
from datetime import timedelta
from .api_config import API_KEY, BASE_URL
from rest_framework import status
from rest_framework.response import Response

class APIService:
    def __init__(self, assets, ticker_period):
        self.assets = assets
        self.ticker_period = ticker_period
        self.headers = {
            #'Accept': 'text/plain',
            'X-CoinAPI-Key': API_KEY
        }
        self.base_url = BASE_URL

    # The objective is to combine intervals of days following a quota of max_days = 100 days according to start_date and end_date (since the free API collects on 100 days/request).
    # date_start / date_end: date objects
    # max_days : int
    # start : 1/1/2024 date boject
    # End : 27/5/2024 date boject 
    #                                                                       
    #                                                                       
    # -> [[1/1/2024, 10/04/2024], [11/04/2024, 27/5/2024]] get_dates_intervals return 100 days

    def get_dates_intervals(self, start_date, end_date, max_days):
        diff = end_date - start_date
        diff_days = abs(diff.days)
        print("There are in total", diff_days, "days between", start_date, "and", end_date)
        dates_intervals = []
        interval_begin_date = start_date

        while diff_days > 0:
            nb_days_to_add = max_days - 1 # max_days - 1 because, logically, the markets return +1 extra day if in the past
            # we already have the closing price. We need to work as if we were on a current date to avoid rigging.
            # Are there really 100 days left?
            if diff_days < max_days - 1:
                nb_days_to_add = diff_days   

            # At the end of the interval, we add what remains to reach 100 days.
            interval_end_date = interval_begin_date + timedelta(nb_days_to_add)
            dates_intervals.append([interval_begin_date, interval_end_date])
            diff_days -= nb_days_to_add + 1  

            # At the end of an interval, move on to the next day in the following interval.
            interval_begin_date = interval_end_date + timedelta(1)

        return dates_intervals

    # Call the API and display the result as it is.
    # start / end_date object date (inclusive)
    def get_exchange_rates(self, start_date, end_date):
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = (end_date + timedelta(1)).strftime("%Y-%m-%d")
        print(f"Collection of new data from {start_date} to {end_date}")
        # url = self.base_url + 'v1/assets'
        url = f"{self.base_url}v1/exchangerate/{self.assets}/history?period_id={self.ticker_period}&time_start={start_date_str}T00:00:00&time_end={end_date_str}T00:00:00"
        
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        
        elif response.status_code == 550:
            # print(f"API Error: Please enter a valid ticker")
            return {"error": "Please enter a valid ticker"}
        
        elif response.status_code == 429:
            print(f"API Error: {response.status_code}")
            return {"error": "This API Key is no longer functional. Please subscribe to another service."}
        
        elif response.status_code == 500:
            print(f"API Error: {response.status_code}")
            return {"error": "The daily quota (100) reserved for data collection is exhausted. Please wait 24 hours."}
        
        else:
            print(f"API Error: {response.status_code}")
            return {"error": {response.status_code}}
        
    # extended : start and end dates can be separeted more than 100 days

    def get_exchange_rates_extended(self, start_date, end_date):
        rates = []
        date_intervals = self.get_dates_intervals(start_date, end_date, 100)
        for interval in date_intervals:
            interval_rates = self.get_exchange_rates(interval[0], interval[1])  # We add the start date and end date respectively of the interval itself.
            if interval_rates:
                rates += interval_rates
        return rates
    
    # I want to reduce error ranges on highs, lows and closes

    def get_filtered_rates(self, start_date, end_date):
        rates = self.get_exchange_rates_extended(start_date, end_date)
        return self.filter_inconsistent_rate_values(rates)

    # After analysis, I realized that APIs can retrieve monetary data with a margin of error on opens, highs, lows and closes.
    # So I wanted to impose a logic according to which the values are spaced by a ratio times 10 or divided by 10. We'll be able to
    # tell whether the values are consistent or not. Among these four values, we'll take the one closest to the previous or next day.
    # If not, take the previous day's value.

    def filter_inconsistent_rate_values(self, input_rates):
        def rate_is_inconsistent(rate):
            v = rate["rate_open"]
            vmin = v / 10
            vmax = v * 10
            if not vmin <= rate["rate_close"] <= vmax:
                return True
            if not vmin <= rate["rate_high"] <= vmax:
                return True
            if not vmin <= rate["rate_low"] <= vmax:
                return True
            return False

        filtered_rates = []
        for i, r in enumerate(input_rates):
            if rate_is_inconsistent(r):
                # take the day before and the day after
                reference_rate = input_rates[i - 1] if i > 0 else input_rates[i + 1]
                r["rate_open"] = reference_rate["rate_open"]
                r["rate_close"] = reference_rate["rate_close"]
                r["rate_high"] = reference_rate["rate_high"]
                r["rate_low"] = reference_rate["rate_low"]
            filtered_rates.append(r)
        return filtered_rates
