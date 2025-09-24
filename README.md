# Career Catalyst

A comprehensive career management system built with FastAPI and MongoDB, featuring opportunity tracking, application management, and professional development tools.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd career-catalyst
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```bash
# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://root:CareerCatalyst123!@localhost:27017
MONGODB_DATABASE_NAME=career_catalyst
MONGODB_TEST_DATABASE_NAME=career_catalyst_test

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Start MongoDB with Docker Compose

Navigate to the docker compose directory and start MongoDB:

```bash
cd docker_compose
docker-compose up -d
```

This will start MongoDB with:
- **Port**: 27017
- **Username**: root
- **Password**: CareerCatalyst123!
- **Data persistence**: Via Docker volume `mongodb_data`

### 4. Install Python Dependencies

```bash
# Install dependencies
pip install -r requirements.txt
```

### 5. Run the Application

From the project root directory:

```bash
# Run the FastAPI application
python app.py
```

The application will start on **http://localhost:8001**

## 📁 Project Structure

```
career-catalyst/
├── src/                          # Source code
│   ├── presentation/            # FastAPI app and API routes
│   │   ├── app.py              # Main FastAPI application
│   │   └── api/                # API route handlers
│   ├── application/            # Application services
│   │   └── services/           # Business logic services
│   ├── domain/                 # Domain entities and interfaces
│   │   ├── entities/           # Domain entities
│   │   ├── interfaces/         # Repository and service interfaces
│   │   └── value_objects/      # Domain value objects
│   └── infrastructure/         # Infrastructure layer
│       ├── database.py         # MongoDB connection management
│       ├── container.py        # Dependency injection
│       └── repositories/       # Data access implementations
├── tests/                      # Test suite
├── docker_compose/             # Docker configuration
│   └── docker-compose.yaml    # MongoDB service definition
├── templates/                  # Frontend templates
├── app.py                     # Application entry point
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_CONNECTION_STRING` | MongoDB connection URI | `mongodb://localhost:27017` |
| `MONGODB_DATABASE_NAME` | Main database name | `career_catalyst` |
| `MONGODB_TEST_DATABASE_NAME` | Test database name | `career_catalyst_test` |
| `FLASK_ENV` | Application environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `True` |

### MongoDB Authentication

The Docker Compose setup creates a MongoDB instance with authentication enabled:

- **Root Username**: `root`
- **Root Password**: `CareerCatalyst123!`
- **Connection String**: `mongodb://root:CareerCatalyst123!@localhost:27017`

## 🐳 Docker Services

### MongoDB Service

```yaml
services:
  mongodb:
    image: mongo:6.0
    container_name: mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: CareerCatalyst123!
    volumes:
      - mongodb_data:/data/db
```

### Docker Commands

```bash
# Start MongoDB service
cd docker_compose
docker-compose up -d

# View logs
docker-compose logs -f mongodb

# Stop services
docker-compose down

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

## 🌐 API Endpoints

Once running, access:

- **Main Application**: http://localhost:8001/
- **API Documentation**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health
- **API Info**: http://localhost:8001/api

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/unit/
pytest tests/integration/

# Run tests with coverage
pytest --cov=src
```

## 📦 Key Dependencies

- **FastAPI**: Modern, fast web framework for APIs
- **Motor**: Async MongoDB driver for Python
- **PyMongo**: MongoDB driver for Python
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation using Python type annotations
- **Python-dotenv**: Environment variable management
- **Pytest**: Testing framework

## 🛠️ Development

### Running in Development Mode

The application runs with auto-reload enabled by default when using `python app.py`.

### Database Initialization

The application automatically:
1. Connects to MongoDB on startup
2. Creates necessary indexes for optimal performance
3. Handles connection errors gracefully

### Adding New Dependencies

```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Install the new package
pip install -r requirements.txt
```

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Ensure MongoDB is running: `docker-compose ps`
   - Check connection string in `.env` file
   - Verify Docker service is healthy: `docker-compose logs mongodb`

2. **Port Already in Use**
   - Check if port 8001 is available: `lsof -i :8001`
   - Change port in `src/presentation/app.py` if needed

3. **Import Errors**
   - Ensure you're running from the project root directory
   - Verify all dependencies are installed: `pip install -r requirements.txt`

### Logs

Application logs are displayed in the console when running in development mode. For production deployment, configure appropriate log handlers.

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]