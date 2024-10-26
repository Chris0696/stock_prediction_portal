from rest_framework import serializers


class StockPredictionSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)  # For example : 'EUR/USD'
    start_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    end_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    ticker_period = serializers.CharField(max_length=10)  # For example : '1DAY', '1HOUR', etc.

    def validate(self, data):
        
        # Validates that the start date is before the end date.
        
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("The start date must be earlier than the end date.")
        return data
    

