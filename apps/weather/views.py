from django.shortcuts import render
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import SearchHistory
from .services import get_weather_data
from .serializers import format_weather_data, SearchHistorySerializer

@extend_schema(
    tags=['weather'],
    summary='Consultar dados do clima',
    description='Retorna dados meteorológicos atualizados para uma cidade específica',
    parameters=[
        OpenApiParameter(
            name='city',
            location=OpenApiParameter.PATH,
            description='Nome da cidade para consultar o clima',
            required=True,
            type=str,
            examples=[
                OpenApiExample(
                    'São Paulo',
                    value='sao%20paulo',
                    description='Exemplo com São Paulo'
                ),
                OpenApiExample(
                    'Rio de Janeiro',
                    value='rio%20de%20janeiro',
                    description='Exemplo com Rio de Janeiro'
                ),
            ]
        )
    ],
    responses={
        200: {
            'description': 'Dados do clima retornados com sucesso',
            'examples': [
                {
                    'application/json': {
                        'cidade': 'São Paulo',
                        'temperatura': 25.5,
                        'descricao': 'Parcialmente nublado',
                        'umidade': 65,
                        'vento': 12.3,
                        'timestamp': '2024-01-15T14:30:00Z'
                    }
                }
            ]
        },
        400: {
            'description': 'Erro ao buscar dados do clima',
            'examples': [
                {
                    'application/json': {
                        'erro': 'Erro ao buscar dados do clima',
                        'mensagem': 'Cidade não encontrada'
                    }
                }
            ]
        }
    }
)
class WeatherAPIView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get(self, request, city):
        cache_key = f"weather_{city.lower()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        try:
            raw_data = get_weather_data(city)
            formatted_data = format_weather_data(raw_data)
            
            cache.set(cache_key, formatted_data, timeout=600)
            SearchHistory.objects.create(city=city)

            return Response(formatted_data)
        except Exception as e:
            # Adicionar logging aqui depois 
            return Response({
                "erro": "Erro ao buscar dados do clima",
                "mensagem": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['history'],
    summary='Consultar histórico de buscas',
    description='Retorna as últimas 10 consultas de clima realizadas',
    responses={
        200: {
            'description': 'Histórico de consultas retornado com sucesso',
            'examples': [
                {
                    'application/json': {
                        'historico': [
                            {
                                'id': 1,
                                'cidade': 'São Paulo',
                                'data_consulta': '2024-01-15T14:30:00Z'
                            }
                        ],
                        'total_consultas': 1
                    }
                }
            ]
        },
        400: {
            'description': 'Erro ao buscar histórico',
            'examples': [
                {
                    'application/json': {
                        'erro': 'Erro ao buscar histórico de consultas',
                        'mensagem': 'Erro interno do servidor'
                    }
                }
            ]
        }
    }
)
class HistoryAPIView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get(self, request):
        try:
            history = SearchHistory.objects.all()[:10]
            serializer = SearchHistorySerializer(history, many=True)
            
            return Response({
                "historico": serializer.data,
                "total_consultas": len(serializer.data)
            })
        except Exception as e:
            return Response({
                "erro": "Erro ao buscar histórico de consultas",
                "mensagem": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        