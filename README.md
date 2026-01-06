# 🏦 Banco Moderno API - Sistema Bancário Full Stack Profissional

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white)](https://jinja.palletsprojects.com/)

Este é um projeto de sistema bancário de alto nível, desenvolvido com foco em performance, segurança e escalabilidade. O sistema oferece uma API robusta utilizando **FastAPI** e uma interface de usuário moderna, responsiva e elegante.

---

## 📸 Screenshots do Sistema

### **Backend & API**
Aqui você pode ver a robustez da nossa API documentada e as operações de banco de dados.

<div align="center">
  <img src="images/backend/3.png" width="90%" />
  <br><br>
  <img src="images/backend/4.png" width="90%" />
  <br><br>
  <img src="images/backend/5.png" width="90%" />
</div>

### **Frontend & Interface**
Uma interface moderna, limpa e focada na experiência do usuário.

<div align="center">
  <img src="images/frontend/1.png" width="95%" />
  <br><br>
  <img src="images/frontend/2.png" width="95%" />
</div>

---

## 🏆 Desafio vs. Entrega Profissional

Este projeto foi além dos requisitos básicos de um desafio técnico comum, implementando padrões de arquitetura e segurança utilizados em sistemas de produção.

| Funcionalidade | Requisito Básico (Comum) | **Entrega (Este Projeto)** |
| :--- | :--- | :--- |
| **Arquitetura** | Script único ou rotas simples | **Service Layer Pattern**: Separação clara de responsabilidades. |
| **Concorrência** | Execução Síncrona | **100% Async/Await**: Alta performance e escalabilidade. |
| **Segurança** | Autenticação simples ou inexistente | **JWT + bcrypt**: Proteção robusta de dados e rotas. |
| **Gestão de Contas** | Apenas uma conta por usuário | **Múltiplas Contas**: Suporte a Conta Corrente e Poupança. |
| **Persistência** | Dados em memória (Dicionários) | **SQLAlchemy 2.0 + SQLite**: Banco de dados relacional real. |
| **Documentação** | Swagger padrão e vazio | **Swagger Customizado**: Exemplos reais e tags organizadas. |
| **Interface** | Apenas via Terminal/Postman | **Frontend Full Stack**: Dashboard moderno e responsivo. |
| **UX & Erros** | Erros brutos (JSON) no alert() | **Toast System**: Notificações elegantes e erros formatados. |
| **DevOps** | Execução manual (python main.py) | **Docker & Makefile**: Automação total do ambiente. |

---

## 🚀 Funcionalidades Principais

### **Gestão de Usuários & Segurança**
*   **Autenticação JWT (OAuth2)**: Fluxo de segurança profissional com tokens de acesso e expiração.
*   **Password Hashing**: Utiliza `bcrypt` com proteção contra ataques de dicionário.
*   **CORS & Security Middlewares**: Configurado para proteção contra ataques comuns da web.

### **Operações Bancárias (Assíncronas)**
*   **Múltiplas Contas**: Suporte dinâmico para Conta Corrente (CC) e Conta Poupança (CP) no mesmo perfil.
*   **Transações Seguras**: Depósitos, saques e transferências com integridade referencial garantida pelo SQLAlchemy.
*   **Validações de Negócio Sênior**: Bloqueio de contas inativas, verificação de saldo em tempo real e limites de segurança.
*   **Extrato Inteligente**: Histórico de transações com paginação de alta performance.

### **Interface (Frontend)**
*   **Dashboard Moderno**: Interface construída com **Tailwind CSS** e **Lucide Icons**.
*   **Experiência SPA-like**: Consumo de API via Fetch API (AJAX) para navegação sem refresh.
*   **Feedback Visual**: Tratamento de erros amigável e notificações de sucesso.

---

## 🛠️ Stack Tecnológica

*   **Backend**: Python 3.10+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2.
*   **Banco de Dados**: SQLite (Assíncrono via `aiosqlite`).
*   **Frontend**: HTML5, Jinja2 Templates, Tailwind CSS, JavaScript (ES6+).
*   **Automação**: Makefile para gestão de ambiente e dependências.

---

## 📦 Como Executar

O projeto utiliza um **Makefile** para simplificar o setup. Siga os passos:

1.  **Instalar dependências**:
    ```bash
    make install
    ```

2.  **Preparar o Banco de Dados (Opcional - se quiser começar do zero)**:
    ```bash
    make db-reset
    ```

3.  **Iniciar o servidor**:
    ```bash
    make run
    ```
    O sistema estará disponível em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 🐳 Rodando com Docker

Se você tiver o Docker instalado, pode subir o sistema completo sem precisar configurar o Python localmente:

1.  **Construir e Iniciar**:
    ```bash
    make docker-build
    make docker-up
    ```
    O sistema estará disponível no mesmo endereço: [http://127.0.0.1:8000](http://127.0.0.1:8000)

2.  **Parar os Containers**:
    ```bash
    make docker-down
    ```

4.  **Documentação Técnica (Swagger)**:
    Explore todos os endpoints em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🏗️ Arquitetura & Padrões de Projeto

O projeto adota uma arquitetura modular baseada em **Camadas (Layered Architecture)** e o padrão **Service Layer**, garantindo que a regra de negócio seja independente do framework web.

### **As Camadas do Sistema**
*   **Camada de Entrada (API Endpoints)**: Localizada em `app/api/`, gerencia apenas as requisições HTTP, validações de contrato (Pydantic) e respostas. Não contém lógica de negócio.
*   **Camada de Serviço (Service Layer)**: Em `app/services/`, reside o "coração" do sistema. Aqui estão as regras de transferências, cálculos de saldo e validações bancárias. É 100% isolada e testável.
*   **Camada de Dados (Models & DB)**: Utiliza **SQLAlchemy 2.0** com sessões assíncronas. Os modelos em `app/models/` definem a estrutura do banco, enquanto `app/db/` gerencia a conexão.
*   **Camada de Esquemas (Schemas)**: Contratos de dados robustos usando **Pydantic v2**, garantindo que nenhum dado inválido entre ou saia da API.
*   **Camada de Segurança (Core)**: Centraliza a lógica de autenticação JWT, hashing de senhas com bcrypt e configurações globais.

### **Fluxo de uma Requisição (Exemplo: Transferência)**
1.  **Client**: Envia um POST para `/api/v1/banking/transfer`.
2.  **Route**: Valida o token JWT e o formato do JSON de entrada.
3.  **Service**: Inicia uma transação atômica, verifica saldos, aplica regras de limites e executa a operação.
4.  **Database**: Persiste as alterações de saldo e registra o extrato de forma assíncrona.
5.  **Response**: Retorna sucesso ou erro formatado via Global Exception Handler.

### **Estrutura de Diretórios**
```text
├── app/
│   ├── api/            # Endpoints (v1) e Injeção de Dependências
│   ├── core/           # Segurança (JWT), Configurações e Logs
│   ├── db/             # Conexão assíncrona com SQLite/aiosqlite
│   ├── models/         # Modelos de dados do SQLAlchemy
│   ├── schemas/        # Modelos Pydantic (Data Transfer Objects)
│   ├── services/       # Regras de Negócio (Service Layer)
│   ├── static/         # Frontend: CSS (Tailwind) e JS (Modular)
│   └── templates/      # Interface: Jinja2 estruturado por módulos
├── tests/              # Testes de integração e fluxo ponta-a-ponta
├── main.py             # Entry point e Handlers de Erros Globais
└── Makefile            # Orquestração de tarefas e automação
```

---
*Desenvolvido como uma demonstração de excelência técnica em Python e Engenharia de Software.*
