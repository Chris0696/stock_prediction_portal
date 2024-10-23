from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StockPredictionResult


class StockPredictionResultAdmin(UserAdmin):
    list_display = ('user', 'ticker', 'start_date', 'end_date', 'ticker_period', 'plot_200_dma_url', 'plot_prediction_url', 'r2')
    ordering = ('created_at',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(StockPredictionResult, StockPredictionResultAdmin)


