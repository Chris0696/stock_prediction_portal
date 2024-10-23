from rest_framework import serializers


class StockPredictionSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)  # Par exemple : 'EUR/USD'
    start_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    end_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    ticker_period = serializers.CharField(max_length=10)  # Par exemple : '1DAY', '1HOUR', etc.

    def validate(self, data):
        
        # Valide que la date de début est avant la date de fin.
        
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La date de début doit être antérieure à la date de fin.")
        return data
    
"""

class RateSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)  # Par exemple : 'EUR/USD'
    start_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    end_date = serializers.DateField()  # Format : 'YYYY-MM-DD'
    ticker_period = serializers.CharField(max_length=10)  # Par exemple : '1DAY', '1HOUR', etc.

    def validate(self, data):
        
        # Valide que la date de début est avant la date de fin.
        
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La date de début doit être antérieure à la date de fin.")
        return data
    
"""

