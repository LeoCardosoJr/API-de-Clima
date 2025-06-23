from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import os
import pdb  # Adicionar import do debugger
from .models import SearchHistory
from .services import get_weather_data
from .serializers import format_weather_data


class WeatherServicesUnitTests(TestCase):
    """Testes unitários para os serviços de clima"""
    
    def setUp(self):
        cache.clear()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_weather_data_api_key_missing(self):
        """Teste: API deve lançar exceção quando a chave da API não está configurada"""
        
        with self.assertRaises(Exception) as context:
            get_weather_data("São Paulo")
            
        self.assertEqual(str(context.exception), "Chave da API não configurada")
    
    @patch('apps.weather.services.requests.get')
    def test_get_weather_data_city_not_found(self, mock_get):
        """Teste: deve lançar exceção quando a cidade não é encontrada"""
        # Mock da resposta da API com código 404 (cidade não encontrada)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'cod': '404',
            'message': 'city not found'
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test_key'}):
            with self.assertRaises(Exception) as context:
                get_weather_data("CidadeInexistente")
            
            self.assertEqual(str(context.exception), "Erro: Cidade não encontrada")
    
    def test_format_weather_data_correct_formatting(self):
        """Teste: deve formatar corretamente os dados da API"""
        # Dados mockados da API OpenWeather
        raw_data = {
            'name': 'São Paulo',
            'main': {
                'temp': 25.67,
                'feels_like': 26.2,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {
                'speed': 3.45,
                'deg': 180
            },
            'sys': {
                'country': 'BR'
            },
            'visibility': 10000
        }
        
        formatted_data = format_weather_data(raw_data)
        
        # Verificar se os dados foram formatados corretamente
        self.assertEqual(formatted_data['cidade'], 'São Paulo')
        self.assertEqual(formatted_data['pais'], 'BR')
        self.assertEqual(formatted_data['temperatura'], 25.7)  # Arredondado
        self.assertEqual(formatted_data['sensacao_termica'], 26.2)  # Arredondado
        self.assertEqual(formatted_data['umidade'], 65)
        self.assertEqual(formatted_data['pressao'], 1013)
        self.assertEqual(formatted_data['velocidade_vento'], 3.5)  # Arredondado
        self.assertEqual(formatted_data['direcao_vento'], 180)
        self.assertEqual(formatted_data['visibilidade'], 10000)


class WeatherAPIIntegrationTests(APITestCase):
    """Testes de integração para as APIs de clima"""
    
    def setUp(self):
        cache.clear()
        SearchHistory.objects.all().delete()
    
    @patch('apps.weather.services.requests.get')
    def test_weather_api_complete_flow_with_cache(self, mock_get):
        """Teste de integração: fluxo completo da API de clima com cache"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'name': 'São Paulo',
            'main': {
                'temp': 25.0,
                'feels_like': 26.0,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {
                'speed': 3.0,
                'deg': 180
            },
            'sys': {
                'country': 'BR'
            },
            'visibility': 10000
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test_key'}):
            # Primeira requisição - deve buscar da API e salvar no cache
            url = reverse('weather', kwargs={'city': 'São Paulo'})
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('cidade', response.data)
            self.assertEqual(response.data['cidade'], 'São Paulo')
            
            # Verificar se foi salvo no cache
            cache_key = "weather_são paulo"
            cached_data = cache.get(cache_key)
            self.assertIsNotNone(cached_data)
            
            # Verificar se foi criado registro no histórico
            history_count = SearchHistory.objects.filter(city='São Paulo').count()
            self.assertEqual(history_count, 1)
            
            # Segunda requisição - deve retornar do cache (não deve chamar a API novamente)
            mock_get.reset_mock()
            response2 = self.client.get(url)
            
            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            # Verificar se a API não foi chamada novamente
            mock_get.assert_not_called()
    
    @patch('apps.weather.services.requests.get')
    def test_weather_api_invalid_city_error(self, mock_get):
        """Teste de integração: erro para cidade inválida"""
        # Mock da resposta da API com erro
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'cod': '404',
            'message': 'city not found'
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test_key'}):
            url = reverse('weather', kwargs={'city': 'CidadeInexistente'})
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('erro', response.data)
            self.assertIn('mensagem', response.data)
            self.assertEqual(response.data['erro'], 'Erro ao buscar dados do clima')
    
    def test_history_api_list_consultations(self):
        """Teste de integração: listagem do histórico de consultas"""
        # Criar alguns registros de histórico
        SearchHistory.objects.create(city='São Paulo')
        SearchHistory.objects.create(city='Rio de Janeiro')
        SearchHistory.objects.create(city='Brasília')
        
        url = reverse('weather_history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('historico', response.data)
        self.assertIn('total_consultas', response.data)
        
        # Verificar se retornou os dados corretos
        self.assertEqual(response.data['total_consultas'], 3)
        self.assertEqual(len(response.data['historico']), 3)
        
        # Verificar se os campos estão corretos
        for item in response.data['historico']:
            self.assertIn('city', item)
            self.assertIn('search_time', item)
