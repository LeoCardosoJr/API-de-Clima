from django.shortcuts import render
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SearchHistory
from .services import get_weather_data
# Importe seu serializer aqui

class WeatherAPIView(APIView):
    # A configuração de Rate Limiting será feita em settings.py
    def get(self, request, city):
        cache_key = f"weather_{city.lower()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        try:
            data = get_weather_data(city)
            cache.set(cache_key, data, timeout=600)
            SearchHistory.objects.create(city=city)

            return Response(data)
        except Exception as e:
            # Adicionar logging aqui depois 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        