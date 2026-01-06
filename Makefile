# Makefile para Banco Moderno API

# Variáveis
PYTHON = python
PIP = $(PYTHON) -m pip
UVICORN = $(PYTHON) -m uvicorn
APP = main:app
HOST = 127.0.0.1
PORT = 8000

.PHONY: help install run stop clean test db-reset docker-build docker-up docker-down

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instala as dependências do projeto"
	@echo "  make run          - Inicia o servidor localmente"
	@echo "  make docker-build - Cria a imagem Docker"
	@echo "  make docker-up    - Sobe o container Docker"
	@echo "  make docker-down  - Para os containers Docker"
	@echo "  make test         - Executa os testes automatizados"
	@echo "  make db-reset     - Apaga o banco de dados e reinicia do zero"

# ... (outros comandos permanecem iguais)

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

install:
	$(PIP) install --upgrade -r requirements.txt

run:
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

stop:
	@echo "Parando o Uvicorn..."
	-taskkill /F /IM python.exe /T

test:
	$(PYTHON) tests/test_api.py

db-reset:
	@echo "Resetando banco de dados..."
	-del sql_app.db
	@echo "Iniciando servidor para recriar tabelas..."
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT)

clean:
	@echo "Limpando cache e temporários..."
	-rmdir /s /q __pycache__
	-rmdir /s /q app\__pycache__
	-rmdir /s /q .pytest_cache
	-del /q *.pyc
