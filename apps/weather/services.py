import requests
import os

def get_weather_data(city: str) -> dict:
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    
    if not api_key:
        raise Exception("Chave da API não configurada")
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        data = response.json()
        
        # Verificar se a cidade não foi encontrada (código 404)
        if data.get('cod') == '404' or data.get('cod') == 404:
            raise Exception("Cidade não encontrada")
        
        # Verificar se há erro na resposta
        if data.get('cod') and data.get('cod') != 200:
            raise Exception(f"Erro da API: {data.get('message', 'Erro desconhecido')}")
            
        return data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro na requisição: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro: {str(e)}")
