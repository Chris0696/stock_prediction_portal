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

    # The objective is to combine intervals of days following a quota of max_days = 100 days according to start_date and end_date (since the API collects on 100 days/request).
    # date_start / date_end: date objects
    # max_days : int
    # start : 1/5/2024
    # End : 19/9/2024
    # -> [[1/5/2024, 10/08/2024], [11/08/2024, 19/09/2024]] 

    def get_dates_intervals(self, start_date, end_date, max_days):
        diff = end_date - start_date
        diff_days = abs(diff.days)
        print("There are in total", diff_days, "days between", start_date, "and", end_date)
        dates_intervals = []
        interval_begin_date = start_date

        while diff_days > 0:
            nb_days_to_add = max_days - 1
            if diff_days < max_days - 1:
                nb_days_to_add = diff_days
            interval_end_date = interval_begin_date + timedelta(nb_days_to_add)
            dates_intervals.append([interval_begin_date, interval_end_date])
            diff_days -= nb_days_to_add + 1
            interval_begin_date = interval_end_date + timedelta(1)

        return dates_intervals

    # Call the API and display the result as it is.

    def get_exchange_rates(self, start_date, end_date):
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = (end_date + timedelta(1)).strftime("%Y-%m-%d")
        print(f"Collection of new data from {start_date} to {end_date}")
        # url = self.base_url + 'v1/assets'
        url = f"{self.base_url}v1/exchangerate/{self.assets}/history?period_id={self.ticker_period}&time_start={start_date_str}T00:00:00&time_end={end_date_str}T00:00:00"
        
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            # print("Your remaining quota is :", response.headers["x-ratelimit-quota-remaining"])
            data = json.loads(response.text)
            # nb_assets = len(data)
            
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
            interval_rates = self.get_exchange_rates(interval[0], interval[1])
            if interval_rates:
                rates += interval_rates
        return rates

    def get_filtered_rates(self, start_date, end_date):
        rates = self.get_exchange_rates_extended(start_date, end_date)
        return self.filter_inconsistent_rate_values(rates)

    # I want to reduce error ranges on highs, lows and closes

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
