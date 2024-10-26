from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import StockPredictionSerializer
from rest_framework import status
from rest_framework.response import Response
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import os
from django.conf import settings
from .utils import save_plot
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from sklearn.metrics import mean_squared_error, r2_score
from .api_service import APIService
from .rates_data_manager import RatesDataManager 
from .rates_data_processing import MovingAverageCalculator
from datetime import date, timedelta, datetime
from .models import StockPredictionResult
from rest_framework.permissions import IsAuthenticated

       
class StockPredictionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        serializer = StockPredictionSerializer(data=request.data)
        if serializer.is_valid():
            ticker = serializer.validated_data['ticker']

            # # Fetch the data from yfinance
            # now = datetime.now()
            # start = datetime(now.year-10, now.month, now.day)
            # end = now
            # df = yf.download(ticker, start, end)
            # #print(df)
            # if df.empty:
            #     return Response({"error": "No Data found for given ticker.", 'status': status.HTTP_404_NOT_FOUND})
            
            # df = df.reset_index()

            # Fetch the data from alogorithm
            
            start_date_normal = serializer.validated_data['start_date']  # Format YYYY-MM-DD
            end_date_normal = serializer.validated_data['end_date']  # Format YYYY-MM-DD

            start_date_str = start_date_normal.strftime("%Y-%#m-%#d") # Format YYYY-M-D
            end_date_str = end_date_normal.strftime("%Y-%#m-%#d")  # Format YYYY-M-D

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() - timedelta(1) # <-- Because we don't yet have the closing price for the current day.

            ticker_period = serializer.validated_data['ticker_period']  # e.g. '1DAY'

            print(f"Ticker: {ticker}, Start Date: {start_date}, End Date: {end_date}, Ticker Period: {ticker_period}")
            # try:
            # Create an instance of RatesDataManager
            # Create an instance of the APIService class

            api_service = APIService(ticker, ticker_period)
            
            # Now, pass the api_service instance as an argument when creating rates_manager
            rates_manager = RatesDataManager(api_service)
            
            #  Call method to retrieve data

            rates = rates_manager.get_and_manage_rates_data(ticker, start_date, end_date, ticker_period)
            
            # Extract rate dates
            
          
            #  Check if API has returned an error (wrong ticker)

            if isinstance(rates, dict) and "error" in rates:
                return Response({"error": rates["error"], 'status': status.HTTP_404_NOT_FOUND})

            #  Check if data has been returned

            if rates is None or len(rates) == 0:
                
                return Response({"error": "No Data found for given ticker.", 'status': status.HTTP_404_NOT_FOUND})
            

            rates_dates = [datetime.strptime(r["Date"], "%Y-%m-%d") for r in rates]
            
            #  Convert rates to Pandas DataFrame

            df = pd.DataFrame(rates)
            print(df)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            
            # Generate Basic Plot
            plt.switch_backend('AGG')
            plt.figure(figsize=(14, 6))
            plt.plot(df['Close'], label='Closing Price')
            plt.title(f"Closing Price of {ticker}")
            plt.xlabel('Years')
            plt.ylabel('Close Price')
            plt.legend()

            # Save the plot to a file
        
            # Ticker name without special characters
            ticker_filename = ticker.replace("/", "")
            
            plot_img_path = f'{ticker_filename}_plot.png'
            plot_img_url = save_plot(ticker_filename, plot_img_path) # I can't retrieve the image's clickable URL in the backend
            

            # 100 Days moving average
            # ma100 = df['Close'].rolling(100).mean()
            ma100_calculator = MovingAverageCalculator(rates, 100)
            ma100  = ma100_calculator.compute_moving_average()
            ma100_values = [r["Close"] for r in ma100]
            plt.switch_backend('AGG')
            plt.figure(figsize=(14, 6))
            plt.plot(df['Close'], label='Closing Price')
            plt.plot(rates_dates, ma100_values, 'r', label='100 DMA')
            
            plt.title(f"100 Days Moving Average of {ticker}")
            plt.xlabel('Years')
            plt.ylabel('Price')
            plt.legend()
            
            plot_100_dma = save_plot(ticker_filename, "100_dma")

            moving_average_intervals = [50, 100, 150, 200]
            moving_average_list = []

            
            for interval in moving_average_intervals:
                calculator = MovingAverageCalculator(rates, interval)
                moving_averages = calculator.compute_moving_average()
                moving_average_list.append((moving_averages, interval))
            
            # Days movings averages
            plt.switch_backend('AGG')
            plt.figure(figsize=(14, 6))
            plt.plot(df['Close'], label='Closing Price')

            for moving_average_item in moving_average_list:
                moving_average_values = [r["Close"] for r in moving_average_item[0]]
                plt.plot(rates_dates, moving_average_values, label=f"MA{moving_average_item[1]}")
            
            plt.title(f"Days Movings Averages of {ticker}")
            plt.xlabel('Years')
            plt.ylabel('Price')
            plt.legend()
            
            plot_200_dma = save_plot(ticker_filename, "200_dma")

            # Splitting data into Training and Testing datasets
            data_traning = pd.DataFrame(df['Close'][0:int(len(df)*0.7)])
            data_testing = pd.DataFrame(df['Close'][int(len(df)*0.7): int(len(df))])

            # Scaling down the data between 0 & 1
            scaler = MinMaxScaler(feature_range=(0, 1))

            # Load ML Model
            model = load_model('stock_prediction_algo_lstm_model.keras')

            # Preparing Test Data
            past_100_days = data_traning.tail(100)
            final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
            input_data = scaler.fit_transform(final_df)

            x_test = []
            y_test = []

            for i in range(100, input_data.shape[0]):
                x_test.append(input_data[i-100: i])
                y_test.append(input_data[i, 0])
            x_test, y_test = np.array(x_test), np.array(y_test)

            #  Making Predictions
            y_predicted = model.predict(x_test)

            # Revert the scaled prices to original price 
            y_predicted = scaler.inverse_transform(y_predicted.reshape(-1, 1)).flatten()
            y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

            print('y_predicted ==>', y_predicted)
            print('y_test ==>', y_test)

            # Plot the final prediction
            
            plt.switch_backend('AGG')
            plt.figure(figsize=(14, 6))
            plt.plot(y_test, 'b', label='Original Price')
            plt.plot(y_predicted, 'r', label='Predicted Price')
            
            plt.title(f"Final Prediction for {ticker}")
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            # Sauvegarde de la prédiction finale
            plot_prediction = save_plot(ticker_filename, "final_prediction")

            # Model Evaluation
            # Mean Squard Error (MSE)

            mse = mean_squared_error(y_test, y_predicted)

            # Root Mean Squared Error (RMSE)
            rmse = np.sqrt(mse)

            # R-Squared
            r2 = r2_score(y_test, y_predicted)

            # Save results in database
            prediction_result = StockPredictionResult.objects.create(
                user=user,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                ticker_period=ticker_period,
                plot_img_url=plot_img_url,
                plot_100_dma_url=plot_100_dma,
                plot_200_dma_url=plot_200_dma,
                plot_prediction_url=plot_prediction,
                mse=mse,
                rmse=rmse,
                r2=r2,
            )
            # Save instance to database
            prediction_result.save()

            return Response({
                'status': 'success',
                'ticker': ticker,
                'start_date': start_date,
                'end_date' : end_date,
                'ticker_period': ticker_period, 
                'plot_img': prediction_result.plot_img_url,
                'plot_100_dma': prediction_result.plot_100_dma_url,
                'plot_200_dma': prediction_result.plot_200_dma_url,
                'plot_prediction': prediction_result.plot_prediction_url,
                'mse': prediction_result.mse,
                'rmse': prediction_result.rmse,
                'r2': prediction_result.r2,

                }, status=status.HTTP_200_OK)
        
