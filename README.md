# Scire

Scire is a multilingual research assistant powered by Ollama and Streamlit. It provides fast research capabilities with automatic profanity filtering, news integration, and support for multiple languages.

## Features

- **Fast Research**: Leverages Ollama's local LLM (`llama3.2:3b`) for quick responses
- **Multilingual Support**: Automatic language detection and translation via Deep Translator
- **News Integration**: Real-time news data from NewsAPI with curated African news sources
- **Profanity Filtering**: Automatic detection and filtering of inappropriate content
- **Web Search**: DuckDuckGo integration for additional research sources
- **RSS Feed Parsing**: Support for news feeds and articles
- **Response Metrics**: Track response times, message count, and filtered content

## Tech Stack

- **Backend**: Python with LangChain + Ollama
- **Frontend**: Streamlit
- **Model**: Llama 3.2 (3B parameters)
- **Containerization**: Docker + Docker Compose
- **Search**: DuckDuckGo, NewsAPI, RSS feeds

## Prerequisites

- Docker
- Docker Compose
- `NEWSAPI_KEY` for news integration (get one free at https://newsapi.org)

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Abandadaniel/scire.git
cd scire
