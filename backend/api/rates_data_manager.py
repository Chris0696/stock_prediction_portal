import json
from os import path
from datetime import datetime, timedelta


class RatesDataManager:
    def __init__(self, api_service):
        self.api_service = api_service

    def load_json_data_from_file(self, filename):
        """Load rates data from the JSON file."""
        with open(filename, "r") as f:
            return json.load(f)

    def save_rates_data_to_file(self, filename, rates_data):
        """Save the rates data to a JSON file."""
        if rates_data:
            with open(filename, "w") as f:
                json.dump(rates_data, f)

    def convert_rates_to_date_value_format(self, rates_data):
        """Convert rates data to the desired date-value format."""
        # print([{"Date": r["time_period_start"][:10], "Close": r["rate_close"]} for r in rates_data])
        return [{"Date": r["time_period_start"][:10], "Close": r["rate_close"]} for r in rates_data]

    def get_and_manage_rates_data(self, assets, start_date, end_date, ticker_period):
        """Helper to generate the file name for saving JSON data."""
        data_filename = assets.replace("/", "_") + ".json"
        
        #  Using the APIService instance to retrieve data

        rates_response = self.api_service.get_exchange_rates(start_date, end_date)
       
        #  If the API returns an error, return error

        if isinstance(rates_response, dict) and "error" in rates_response:
            return rates_response  # Contient un message d'erreur

        #  If data is empty or None, return None
        if not rates_response:
            return None
    
        rates = []

        exclude_nb_days_start = 0
        exclude_nb_days_end = 0

        if path.exists(data_filename):
            rates = self.load_json_data_from_file(data_filename)
            if rates:
                print("The json file exists")
                print("    Start date of last data backup", rates[0]["Date"])
                print("    End date of last data backup", rates[-1]["Date"])
                # Convert str date to date objet
                saved_data_date_start = datetime.strptime(rates[0]["Date"], "%Y-%m-%d").date()
                saved_data_date_end = datetime.strptime(rates[-1]["Date"], "%Y-%m-%d").date()

                # Is the new end_date greater than the one already saved (saved_data_date_end)?
                if start_date < saved_data_date_start:
                    print(f"Fetching data from {start_date} to {saved_data_date_start - timedelta(1)}")
                    # - so we make calls to the api (before) ←-- pass the 100-day limit
                    rates_start = self.api_service.get_filtered_rates(start_date, saved_data_date_start - timedelta(1))
                    # saved_data_date_start - timedelta(1) because we don't want to include an existing date
                    rates = self.convert_rates_to_date_value_format(rates_start) + rates

                elif start_date > saved_data_date_start:
                    exclude_nb_days_start = (start_date - saved_data_date_start).days

                # Is the new end_date greater than the one already saved (saved_data_date_end)?
                if end_date > saved_data_date_end:
                    print(f"Fetching data from {saved_data_date_end + timedelta(1)} to {end_date}")
                    rates_end = self.api_service.get_filtered_rates(saved_data_date_end + timedelta(1), end_date)
                    # saved_data_date_end + timedelta(1) because we don't want to include an existing date
                    rates += self.convert_rates_to_date_value_format(rates_end)

                elif end_date < saved_data_date_end:
                    exclude_nb_days_end = (saved_data_date_end - end_date).days

                # Consolidate data (update json file)
                self.save_rates_data_to_file(data_filename, rates)
            else:
                rates = self._fetch_and_save_rates(data_filename, assets, start_date, end_date)
        else:
            rates = self._fetch_and_save_rates(data_filename, assets, start_date, end_date)

        if exclude_nb_days_start > 0:
            rates = rates[exclude_nb_days_start:]  # if exclude_nb_days_start = 5, delete 5 first values.

        if exclude_nb_days_end > 0:
            rates = rates[:-exclude_nb_days_start]  # if exclude_nb_days_end = 5, delete last 5 values.


        return rates

    def _fetch_and_save_rates(self, filename, assets, start_date, end_date):
        rates = self.api_service.get_filtered_rates(start_date, end_date)
        rates = self.convert_rates_to_date_value_format(rates)
        self.save_rates_data_to_file(filename, rates)
        return rates