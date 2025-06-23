# API de Clima

API REST para consulta do clima atual de cidades, utilizando a OpenWeatherMap API.

## Como rodar localmente

1. **Pré-requisitos**  
   - Docker e Docker Compose instalados
   - Conta gratuita na [OpenWeatherMap](https://openweathermap.org/api) para obter a chave da API

2. **Configuração**  
   - Clone o repositório:
     ```bash
     git clone <seu-fork>
     cd API-de-Clima
     ```
   - Crie um arquivo `.env` na raiz com:
     ```
     OPENWEATHER_API_KEY=<sua-chave>
     ```
   - Suba os serviços:
     ```bash
     docker-compose up --build
     ```

3. **Acessos**  
   - API de consulta de clima: http://localhost:8000/weather/
   - API de histórico de clima: http://localhost:8000/weather/weather/history/
   - Swagger: http://localhost:8000/docs/

4. **Testes**
   ```bash
   docker-compose exec app python manage.py test
   ```

## Decisões técnicas principais

- **Estrutura de pastas modularizada (`apps/`)**: Escolhida para facilitar a organização, escalabilidade e separação de responsabilidades. Permite adicionar novos módulos/apps no futuro sem comprometer a estrutura do projeto, tornando o código mais limpo e fácil de manter em projetos maiores.
- **Variáveis de ambiente com valores default**: Para diminuir a quantidade de passos e facilitar o desenvolvimento local, todas as variáveis de ambiente possuem valores padrão. Em produção, recomenda-se sobrescrever todas as variáveis para garantir segurança e configuração adequada.
- **Django REST Framework**: Para construção rápida e robusta de APIs REST.
- **Redis**: Utilizado para cache das respostas da API externa por 10 minutos, reduzindo chamadas e melhorando performance.
- **PostgreSQL**: Banco de dados principal para histórico de consultas.
- **Docker Compose**: Facilita o setup local com todos os serviços necessários.
- **Rate Limiting**: Implementado de forma simples via cache/Redis.
- **Histórico**: Armazena as últimas 10 consultas por usuário/IP.
- **Testes**: Inclui testes unitários e de integração para garantir funcionamento dos principais fluxos.

## O que faria com mais tempo

- Melhoraria as configurações do settings.py para aumentar a segurança em produção (ex: variáveis obrigatórias, CORS restrito, DEBUG desativado, etc).
- Deploy automatizado (CI/CD) com github actions.
- Adicionaria logs estruturados.
- Adicionaria monitoramento e alertas.
- Implementaria autenticação de usuários.
- Melhoraria o rate limiting para ser mais flexível e configurável.

## Assumptions e limitações

- O cache é global por cidade, não por usuário.
- O rate limiting é básico, apenas para evitar abuso simples.
- O histórico é limitado às últimas 10 consultas globais.
- Não há autenticação implementada.
- A API depende da disponibilidade do serviço externo OpenWeatherMap.

