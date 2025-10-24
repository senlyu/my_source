# my_source

`my_source` is a powerful and scalable Python application designed to aggregate information from various sources, process it using Generative AI, and generate insightful reports. This project serves as a demonstration of how to build a robust, maintainable, and AI-powered data processing pipeline.

A live example of this project in action can be found on my [personal blog](https://senlyu.com/blog/categories/Auto-Reports/), where it generates daily financial reports in Chinese.

For a deep dive into the technical architecture and design decisions, please refer to the [PROJECT_DETAILS.md](PROJECT_DETAILS.md) file.

## Features

- **Modular and Scalable Architecture:** The project is built with a clear separation of concerns, making it easy to extend and maintain.
- **Sophisticated AI Integration:** It features advanced AI integration with Google's Gemini models, including:
    - **API Key Management:** Efficiently and securely manages API keys.
    - **Model Fallbacks:** A robust strategy for handling API errors and managing costs.
    - **Caching:** Caches AI model results to reduce latency and API costs.
    - **Prompt Engineering:** A sophisticated system for dynamically generating and managing prompts.
- **Robust Scheduling:** A flexible scheduling system for running tasks at specific times or intervals.
- **Asynchronous by Design:** Leverages `asyncio` for efficient handling of I/O-bound operations.
- **Maintainable and Concurrent:** Designed for maintainability, even with multiple asynchronous sessions, thanks to session-based logging and encapsulated asynchronous logic.

## Technical Stack

- **Python 3.13**
- **`asyncio`** for asynchronous programming
- **`google-generativeai`** for AI integration
- **`telethon`** for interacting with Telegram
- **`pipenv`** for dependency management

## Getting Started

### Prerequisites

- Python 3.13
- `pipenv`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/my_source.git
   cd my_source
   ```

2. Install the dependencies using `pipenv`:
   ```bash
   pipenv install
   ```

### Configuration

Before running the application, you need to create a `config.json` file in the project root. A template for this file is provided in `config.example.json`.

1. Copy the example configuration file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit the `config.json` file and replace the placeholder values with your actual credentials and settings.

### Usage

The application can be started using the `start.sh` script. You need to provide the environment as an argument. The available environments are `prod`, `dev`, `dev_listener`, `dev_reporter`, and `dev_model`.

For example, to run the application in production mode:

```bash
./start.sh prod
```

To run in development mode:

```bash
./start.sh dev
```
