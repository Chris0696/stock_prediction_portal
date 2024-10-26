from rest_framework import serializers


class StockPredictionSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)  # For exemple : 'EUR/USD'
    start_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    end_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    ticker_period = serializers.CharField(max_length=10)  # For exemple : '1DAY', '1HOUR', etc.

    def validate(self, data):
        
        # Validates that the start date is before the end date.
        
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La date de début doit être antérieure à la date de fin.")
        return data
    

