from django.db import models
from accounts.models import User


class StockPredictionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_requests')
    ticker = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    ticker_period = models.CharField(max_length=10)
    plot_img_url = models.URLField(max_length=200)
    plot_100_dma_url = models.URLField(max_length=200)
    plot_200_dma_url = models.URLField(max_length=200)
    plot_prediction_url = models.URLField(max_length=200)
    mse = models.FloatField()
    rmse = models.FloatField()
    r2 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Results for {self.ticker} from {self.start_date} to {self.end_date} by {self.user.username}"

