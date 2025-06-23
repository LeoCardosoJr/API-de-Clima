from rest_framework import serializers
from .models import SearchHistory


def format_weather_data(raw_data):
    main = raw_data.get('main', {})
    wind = raw_data.get('wind', {})
    sys = raw_data.get('sys', {})
    
    return {
        'cidade': raw_data.get('name', ''),
        'pais': sys.get('country', ''),
        'temperatura': round(main.get('temp', 0), 1),
        'sensacao_termica': round(main.get('feels_like', 0), 1),
        'umidade': main.get('humidity', 0),
        'pressao': main.get('pressure', 0),
        'velocidade_vento': round(wind.get('speed', 0), 1),
        'direcao_vento': wind.get('deg', 0),
        'visibilidade': raw_data.get('visibility', 0)
    }


class SearchHistorySerializer(serializers.ModelSerializer):
    search_time = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    
    class Meta:
        model = SearchHistory
        fields = ['city', 'search_time']
        