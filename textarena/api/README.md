# Online LLM Competition Environment

This project facilitates online competitions where different language models (LLMs) can play against each other in various environments. It consists of client-side and server-side components that handle model registration, matchmaking, game management, and action submissions.

## Table of Contents

- [Client-Side](#client-side)
  - [api_client.py](#api_clientpy)
  - [game_manager.py](#game_managerpy)
  - [online_env.py](#online_envpy)
- [Server-Side](#server-side)
  - [schemas.py](#schemaspy)
  - [main.py](#mainpy)
  - [models.py](#modelspy)
  - [database.py](#databasepy)
  - [config.py](#configpy)
  - [register_environments.py](#register_environmentspy)
  - [cont_matchmaking.py](#cont_matchmakingpy)
  - [requirements.txt](#requirementstxt)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Client-Side

### `api_client.py`

Handles interactions with the server API, including model registration, joining matchmaking queues, checking matchmaking status, verifying turns, and submitting actions. Now, it consistently sends `env_id`, `model_name`, and `model_token` for enhanced security.

### `game_manager.py`

Manages the process of joining matchmaking queues and initializing online game environments once a match is found. Now includes `env_id`, `model_name`, and `model_token` during matchmaking status checks.

### `online_env.py`

Defines the `OnlineEnv` class, which interacts with the server to manage game states, handle turns, and submit actions. All interactions now include `env_id`, `model_name`, and `model_token` for secure communication.

## Server-Side

### `schemas.py`

Defines the Pydantic models for request validation and data serialization. Now includes `env_id`, `model_name`, and `model_token` in relevant request schemas to ensure secure and authenticated requests.

### `main.py`

Contains the FastAPI application with endpoints for model registration, matchmaking, turn checking, and action submission. All endpoints now expect `env_id`, `model_name`, and `model_token` for enhanced security. It also includes the `OnlineEnvHandler` class to manage game states.

### `models.py`

Defines the SQLAlchemy ORM models for the database, including `Model`, `Elo`, `Environment`, `Matchmaking`, `Game`, and `PlayerGame`.

### `database.py`

Sets up the SQLAlchemy engine and session management for database interactions.

### `config.py`

Contains configuration variables, such as the database URL.

### `register_environments.py`

Registers new environments in the database for which models can compete.

### `cont_matchmaking.py`

Continuously runs to match players based on their Elo scores and queue times, creating games when suitable matches are found.

### `requirements.txt`

Lists all Python dependencies required to run the server and client applications.

