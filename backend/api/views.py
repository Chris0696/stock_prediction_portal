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
from .rates_data_manager import RatesDataManager  # Import de la classe que nous venons de créer
from datetime import date, timedelta, datetime
from .models import StockPredictionResult
from rest_framework.permissions import IsAuthenticated

"""
class RatesAPIView(APIView):
    def post(self, request):
        serializer = RateSerializer(data=request.data)
        if serializer.is_valid():
        # Récupérer les paramètres du frontend
            ticker = serializer.validated_data['ticker']  #e.g. 'EUR/USD'

            start_date_normal = serializer.validated_data['start_date']  # Format YYYY-MM-DD
            end_date_normal = serializer.validated_data['end_date']  # Format YYYY-MM-DD

            start_date_str = start_date_normal.strftime("%Y-%#m-%#d") # Format YYYY-M-D
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

            end_date_str = end_date_normal.strftime("%Y-%#m-%#d")  # Format YYYY-M-D
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() - timedelta(1)

            ticker_period = serializer.validated_data['ticker_period']  # e.g. '1DAY'
            
            
            print(f"Ticker: {ticker}, Start Date: {start_date}, End Date: {end_date}, Ticker Period: {ticker_period}")
            try:
                # Créer une instance de RatesDataManager
                # Créez une instance de la classe APIService 
                api_service = APIService(ticker, ticker_period)
                # Maintenant, passez l'instance api_service en argument lors de la création de rates_manager
                rates_manager = RatesDataManager(api_service)

                # Appel à la méthode pour récupérer les données
                rates = rates_manager.get_and_manage_rates_data(ticker, start_date, end_date, ticker_period)

                # # Validation de base
                if not ticker or not start_date or not end_date or not ticker_period:
                    return Response({"error": "All parameters (ticker, start_date, end_date, ticker_period) are required."}, status=status.HTTP_400_BAD_REQUEST)

                
                if rates is None:
                    return Response({"error": "No data found for the specified parameters."}, status=status.HTTP_404_NOT_FOUND)
                
                return Response({
                    'ticker': ticker,
                    'start_date': start_date,
                    'end_date' : end_date,
                    'ticker_period': ticker_period,
                    }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({"error": str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Les données ne sont pas valides
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
       


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
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() - timedelta(1)

            ticker_period = serializer.validated_data['ticker_period']  # e.g. '1DAY'

            print(f"Ticker: {ticker}, Start Date: {start_date}, End Date: {end_date}, Ticker Period: {ticker_period}")
            try:
                # Create an instance of RatesDataManager
                # Create an instance of the APIService class
 
                api_service = APIService(ticker, ticker_period)
                
                # Now, pass the api_service instance as an argument when creating rates_manager
                rates_manager = RatesDataManager(api_service)
                
                #  Call method to retrieve data

                rates = rates_manager.get_and_manage_rates_data(ticker, start_date, end_date, ticker_period)
                
                #  Check if API has returned an error (wrong ticker)

                if isinstance(rates, dict) and "error" in rates:
                    return Response({"error": rates["error"], 'status': status.HTTP_404_NOT_FOUND})

                #  Check if data has been returned

                if rates is None or len(rates) == 0:
                    return Response({"error": "No Data found for given ticker.", 'status': status.HTTP_404_NOT_FOUND})
        
            
            except Exception as e:
                return Response({"error": str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
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
            plt.xlabel('Days')
            plt.ylabel('Close Price')
            plt.legend()

            # Save the plot to a file
            ticker_filename = ticker.replace("/", "")
            print(ticker_filename)
            plot_img_path = f'{ticker_filename}_plot.png'
            plot_img_url = save_plot(plot_img_path) # I can't retrieve the image's clickable URL in the backend
            print(plot_img_url)

        
            # 100 Days moving average
            ma100 = df['Close'].rolling(100).mean()
            plt.switch_backend('AGG')
            plt.figure(figsize=(14, 6))
            plt.plot(df['Close'], label='Closing Price')
            plt.plot(ma100, 'r', label='100 DMA')
            plt.title(f"100 Days Moving Average of {ticker}")
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker_filename}_100_dma.png'
            plot_100_dma = save_plot(plot_img_path)

            # 200 Days moving average
            ma200 = df['Close'].rolling(200).mean()
            plt.switch_backend('AGG')
            plt.figure(figsize=(14, 6))
            plt.plot(df['Close'], label='Closing Price')
            plt.plot(ma100, 'r', label='100 DMA')
            plt.plot(ma200, 'g', label='200 DMA')
            plt.title(f"200 Days Moving Average of {ticker}")
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker_filename}_200_dma.png'
            plot_200_dma = save_plot(plot_img_path)

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
            plot_img_path = f'{ticker_filename}_final_prediction.png'
            plot_prediction = save_plot(plot_img_path)

            # Model Evaluation
            # Mean Squard Error (MSE)

            mse = mean_squared_error(y_test, y_predicted)

            # Root Mean Squared Error (RMSE)
            rmse = np.sqrt(mse)

            # R-Squared
            r2 = r2_score(y_test, y_predicted)

            # Enregistrer les résultats dans la base de données
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
        
