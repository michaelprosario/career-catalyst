# Career Catalyst FastAPI Application

A comprehensive career management system built with FastAPI, featuring opportunity tracking, application management, and professional development tools.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or remote instance)

### 1. Set Up Virtual Environment

Create and activate a Python virtual environment:

```bash
# Using venv (recommended)
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root with your configuration:

```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=career_catalyst

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

### 4. Start the Application

From the project root directory:

```bash
# Option 1: Using the built-in runner
python -c "from src.presentation.app import run_app; run_app()"

# Option 2: Using uvicorn directly
uvicorn src.presentation.app:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using the main app.py (if available)
python app.py
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
src/
├── presentation/           # FastAPI application layer
│   ├── app.py             # Main FastAPI application
│   ├── api/               # API route controllers
│   │   └── user_opportunity_controller.py
│   └── schemas/           # Pydantic request/response models
├── application/           # Business logic layer
│   └── services/          # Application services
├── domain/               # Domain entities and business rules
│   ├── entities/         # Domain entities
│   ├── interfaces/       # Repository and service interfaces
│   └── value_objects/    # Domain value objects
└── infrastructure/       # Data access and external services
    ├── container.py      # Dependency injection container
    ├── database.py       # Database configuration
    └── repositories/     # Data repository implementations
```

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Welcome message and API information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### User Opportunities Management

- `POST /api/user-opportunities` - Create a new opportunity
- `GET /api/user-opportunities` - List all opportunities with filtering
- `GET /api/user-opportunities/{opportunity_id}` - Get specific opportunity
- `PUT /api/user-opportunities/{opportunity_id}` - Update opportunity
- `DELETE /api/user-opportunities/{opportunity_id}` - Delete opportunity
- `POST /api/user-opportunities/search` - Search opportunities with advanced criteria

## 🗄️ Database Setup

The application uses MongoDB for data persistence. Ensure you have MongoDB running:

### Local MongoDB
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt update
sudo apt install mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Docker MongoDB
```bash
# Run MongoDB in Docker
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

### MongoDB Atlas (Cloud)
Update your `.env` file with your Atlas connection string:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/career_catalyst?retryWrites=true&w=majority
```

## 🧪 Testing

Run the application tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test files
pytest tests/unit/application/
pytest tests/unit/infrastructure/
```

## 🛠️ Development

### Code Quality Tools

Install development dependencies:
```bash
pip install black isort flake8 mypy
```

Format and lint code:
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

### Hot Reload Development

The application supports hot reload when running with `--reload` flag:
```bash
uvicorn src.presentation.app:app --host 0.0.0.0 --port 8000 --reload
```

Any changes to the Python files will automatically restart the server.

## 📊 Key Features

- **Opportunity Management**: Create, update, and track job opportunities
- **Application Tracking**: Monitor application status and progress
- **Search & Filtering**: Advanced search capabilities with multiple criteria
- **RESTful API**: Clean, well-documented REST endpoints
- **Data Validation**: Robust request/response validation with Pydantic
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Monitoring**: Built-in health check endpoints

## 🔍 API Usage Examples

### Create a New Opportunity
```bash
curl -X POST "http://localhost:8000/api/user-opportunities" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "salary_min": 120000,
    "salary_max": 180000,
    "opportunity_type": "full_time",
    "status": "active"
  }'
```

### Get All Opportunities
```bash
curl "http://localhost:8000/api/user-opportunities"
```

### Search Opportunities
```bash
curl -X POST "http://localhost:8000/api/user-opportunities/search" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco"
  }'
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port in the uvicorn command or kill the process using port 8000
2. **Database Connection Failed**: Ensure MongoDB is running and the connection string is correct
3. **Import Errors**: Make sure you're running from the project root and the virtual environment is activated
4. **Module Not Found**: Install dependencies with `pip install -r requirements.txt`

### Logs

Check application logs for detailed error information. Logs are configured to show INFO level and above.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

[Add your license information here]