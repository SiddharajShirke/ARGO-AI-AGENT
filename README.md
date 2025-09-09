# 🌊 Indian Ocean ARGO AI Agent

**A complete AI-powered system for analyzing Indian Ocean oceanographic data with HTML frontend, FastAPI backend, PostgreSQL database, and ChromaDB vector search.**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)]()
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Search-purple)]()

## 🎯 **System Overview**

The Indian Ocean ARGO AI Agent is a complete oceanographic data analysis system that combines:

- **🤖 AI-Powered Queries**: Natural language processing for complex oceanographic questions
- **🌐 Modern Web Interface**: HTML/CSS/JavaScript frontend with real-time API communication  
- **🚀 FastAPI Backend**: High-performance Python backend with comprehensive API endpoints
- **🗄️ PostgreSQL Database**: Robust relational database for oceanographic profiles and metadata
- **🔍 ChromaDB Vector Search**: Semantic search across oceanographic datasets using embeddings
- **📊 Multi-Format Data Support**: NetCDF files, time series, and spatial data processing
- **🌍 Multilingual Support**: Query processing in English, Hindi, Bengali, Tamil, and Telugu

## 🏗️ **Current System Architecture**

```
🌊 Indian Ocean ARGO AI Agent
├── 🌐 Frontend (HTML/JS)     → Port 3005
├── 🚀 Backend (FastAPI)      → Port 8002  
├── 🗄️ PostgreSQL Database    → Port 5432
└── 🔍 ChromaDB Vector DB     → Port 8001
```

### **✅ Production-Ready Components**

| Component | Technology | Status | Port |
|-----------|------------|--------|------|
| **Frontend** | HTML/CSS/JavaScript | ✅ Working | 3005 |
| **Backend** | FastAPI + Python | ✅ Working | 8002 |
| **Database** | PostgreSQL | ✅ Connected | 5432 |
| **Vector DB** | ChromaDB | ✅ Connected | 8001 |
| **AI Agent** | LangChain + Gemini | ✅ Ready | - |

## 🚀 **Quick Start Commands**

### **🎯 Start Complete System** (Recommended)
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start both frontend and backend
python start_complete.py
```

**Access Points:**
- **Frontend**: http://localhost:3005
- **Backend API**: http://localhost:8002  
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health

### **🔧 Backend Only**
```bash
# Start only the FastAPI backend
python -m app.main
```

### **🌐 Frontend Only**  
```bash
# Start only the HTML frontend
python start_html_frontend.py
```

### **🐳 Docker Services** (Prerequisites)
```bash
# Start database services
docker-compose up -d postgres chromadb
```

## 📋 **System Requirements**

### **Prerequisites**
- **Python 3.11+**
- **Docker & Docker Compose** (for databases)
- **8GB+ RAM** (recommended)
- **2GB+ free disk space**

### **Environment Setup**
```bash
# 1. Clone repository
git clone <repository-url>
cd argo-ai-agen

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies  
pip install -r requirements.txt

# 4. Start database services
docker-compose up -d postgres chromadb

# 5. Configure environment (create .env file)
GOOGLE_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/argo_db
CHROMA_HOST=localhost
CHROMA_PORT=8001

# 6. Start system
python start_complete.py
```

## 🧪 **Testing System Functionality**

### **🔍 Health Checks**
```bash
# Check backend health
curl http://localhost:8002/health
# Expected: {"status":"healthy","phase":"2_complete","ready_for_phase_3":true}

# Check system status  
curl http://localhost:8002/api/v2/system-status
# Expected: {"database":{"status":"healthy"},"vector_database":{"status":"healthy"}...}

# Check available regions
curl http://localhost:8002/api/v2/regions
# Expected: {"regions":[{"id":"arabian_sea","name":"Arabian Sea"...}]}
```

### **🌐 Frontend Testing**
1. Open http://localhost:3005
2. Navigate through different sections
3. Test API connectivity in browser console
4. Verify data loading and visualization

### **🗄️ Database Testing**
```bash
# Check PostgreSQL connection
docker exec -it argo-ai-agen-postgres-1 psql -U user -d argo_db -c "\dt"

# Check ChromaDB collections
curl http://localhost:8001/api/v1/collections
```

## 📁 **Project Structure**

```
argo-ai-agen/
├── 📁 app/                    # Main application package
│   ├── 🚀 main.py            # ✅ PRIMARY BACKEND ENTRY POINT
│   ├── 📁 api/              
│   │   ├── 🛣️ simple_endpoints.py  # ✅ PRIMARY API ENDPOINTS  
│   │   └── 📝 models.py      # Pydantic models
│   ├── 📁 core/             
│   │   ├── ⚙️ config.py       # Configuration management
│   │   ├── 🗄️ database.py     # PostgreSQL operations
│   │   └── 🔍 vector_db.py    # ChromaDB operations
│   ├── 📁 agent/            
│   │   ├── 🤖 workflow.py     # AI agent workflow
│   │   ├── 🧠 llm.py         # LLM provider (Gemini)
│   │   ├── 📚 rag.py         # RAG implementation
│   │   └── 🌍 multilingual.py # Multi-language support
│   ├── 📁 data/             
│   │   ├── 🌊 processor.py    # NetCDF data processing
│   │   ├── 🔢 embeddings.py   # Vector embeddings
│   │   └── 📊 samples.py      # Sample data management
│   └── 📁 utils/             # Utility functions
├── 📁 static/                # ✅ HTML FRONTEND
│   ├── 📄 index.html         # Main HTML page
│   ├── 📁 scripts/           # JavaScript files
│   │   ├── 🌐 api.js         # API client
│   │   └── 📁 components/    # UI components
│   └── 📁 styles/            # CSS styling
├── 📁 scripts/               # Setup & deployment
│   ├── ⚙️ setup.py           # Production setup
│   ├── 🔍 system_check.py    # Health validation
│   └── 🚀 deploy.py          # Deployment automation
├── 📁 tests/                 # Test suite
├── 📁 data/                  # Data storage
├── 🚀 start_complete.py      # ✅ MAIN STARTUP SCRIPT
├── 🌐 start_html_frontend.py # Frontend server
├── 🐳 docker-compose.yml     # Database services
└── 📋 requirements.txt       # Dependencies
```

## 🔌 **API Endpoints**

### **🏥 Health & Status**
- `GET /health` - System health check
- `GET /api/v2/system-status` - Detailed system status

### **🌍 Data Endpoints**  
- `GET /api/v2/regions` - Available ocean regions
- `GET /api/v2/profiles` - ARGO profile data
- `POST /api/v2/query` - Natural language queries

### **📊 Analytics**
- `GET /api/v2/system-status` - Performance metrics
- `GET /api/v2/health` - Component health status

## 🔮 **Next Steps & Roadmap**

### **🎯 Immediate Enhancements**
1. **📊 Add Sample Data**: Populate database with real ARGO profiles
   ```bash
   python scripts/populate.py
   ```

2. **🔒 Add Authentication**: Implement user authentication system
3. **🌐 WebSocket Support**: Enable real-time chat functionality  
4. **📈 Performance Monitoring**: Add metrics and logging dashboard

### **🚀 Future Development**
1. **🤖 Enhanced AI Features**: Advanced query understanding and response generation
2. **📊 Advanced Visualizations**: Interactive charts and maps
3. **📱 Mobile Interface**: Responsive design improvements
4. **🔄 Real-time Data**: Live ARGO data ingestion pipeline
5. **🌍 Geographic Expansion**: Support for other ocean regions

### **🏗️ Technical Improvements**
1. **🧪 Comprehensive Testing**: Expand test coverage
2. **🐳 Full Containerization**: Docker images for all components
3. **☁️ Cloud Deployment**: AWS/GCP deployment configurations
4. **📊 Monitoring**: Production monitoring and alerting

## 🛠️ **Development Guide**

### **🔧 Adding New API Endpoints**
Edit `app/api/simple_endpoints.py`:
```python
@app.get("/api/v2/new-endpoint")
async def new_endpoint():
    return {"message": "New endpoint"}
```

### **🎨 Frontend Development**
- Edit HTML: `static/index.html`
- Edit JavaScript: `static/scripts/`
- Edit CSS: `static/styles/`

### **🗄️ Database Schema Changes**
Edit `app/core/database.py` and run:
```bash
python scripts/setup.py
```

### **🔍 Vector Search Enhancements**
Edit `app/core/vector_db.py` for ChromaDB operations.

## 🚨 **Troubleshooting**

### **🔥 Common Issues**

#### **Port Already in Use**
```bash
# Kill processes on specific ports
netstat -ano | findstr :8002
taskkill /PID <PID> /F
```

#### **Database Connection Failed**
```bash
# Restart database services
docker-compose restart postgres chromadb
```

#### **WebSocket 404 Errors** ✅ RESOLVED
WebSocket functionality is temporarily disabled in frontend to prevent 404 errors. Backend WebSocket endpoints will be implemented in future updates.

#### **Import Errors**
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **🔍 System Validation**
```bash
# Run comprehensive system check
python scripts/system_check.py

# Run integration tests
python scripts/integration_test.py
```

## 🎉 **Success Metrics**

### **✅ System Working Indicators**
- ✅ Frontend loads at http://localhost:3005
- ✅ Backend responds at http://localhost:8002/health  
- ✅ Database connections active
- ✅ API endpoints returning data
- ✅ Vector search operational

### **📊 Performance Benchmarks**
- **API Response Time**: < 500ms average
- **Database Queries**: < 100ms average  
- **Vector Search**: < 200ms average
- **Frontend Load Time**: < 2 seconds

## 📞 **Support & Contributing**

### **🐛 Issue Reporting**
- Check troubleshooting section first
- Run system validation scripts
- Include log files from `logs/` directory

### **🤝 Contributing**
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

### **📝 Documentation**
- Keep README.md updated
- Document new API endpoints
- Update PROJECT_STRUCTURE.md for architecture changes

---

**🌊 Built with ❤️ for oceanographic research and AI-powered data analysis**

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd argo-ai-agent

# Run setup script
python app/scripts/setup.py
```

### 2. Configure Environment

Edit `.env` file with your configurations:

```env
# Database
DB_PASSWORD=your_secure_password

# API Keys (Optional)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Security
SECRET_KEY=your_secret_key
```

### 3. Start Services

```bash
# Start all services (Backend + Dashboard)
python app/main.py

# Or start individually
python app/main.py --mode backend    # API only
python app/main.py --mode dashboard  # Dashboard only
```

### 4. Access Applications

- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💻 Usage

### API Examples

```bash
# Health check
curl http://localhost:8000/health

# Query Argo data
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me temperature data for the Indian Ocean in 2023"}'

# Get available datasets
curl http://localhost:8000/api/datasets
```

### Dashboard Features

1. **Data Explorer**: Browse and filter Argo datasets
2. **AI Query Interface**: Ask questions in natural language
3. **Visualization Tools**: Interactive maps and charts
4. **Data Export**: Download results in various formats

### Command Line Tools

```bash
# Check system dependencies
python app/main.py --check-deps

# Initialize database
python app/main.py --init-db

# Debug mode
python app/main.py --debug
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode | `development` |
| `DEBUG` | Debug mode | `true` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `indian_ocean_argo` |
| `REDIS_HOST` | Redis host | `localhost` |
| `CHROMADB_HOST` | ChromaDB host | `localhost` |
| `API_PORT` | API server port | `8000` |
| `DASHBOARD_PORT` | Dashboard port | `8501` |

### Database Configuration

The system uses three databases:

1. **PostgreSQL**: Primary data storage for Argo float data
2. **Redis**: Caching and session management
3. **ChromaDB**: Vector embeddings for AI search

### LLM Configuration

Supports multiple LLM providers:

- **OpenAI**: GPT-3.5, GPT-4 models
- **Google Gemini**: Gemini Pro models
- **Local Models**: Configurable for local deployment

## 🚀 Deployment

### Development

```bash
# Start development environment
python app/main.py --debug
```

### Production

```bash
# Setup production configuration
python app/scripts/deploy.py setup

# Deploy to production
python app/scripts/deploy.py deploy-prod

# Monitor services
python app/scripts/deploy.py status
```

### Docker Compose

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/test_agent.py
pytest tests/test_pipeline.py
```

### Integration Tests

```bash
# Test database connections
python app/main.py --check-deps

# Test API endpoints
curl http://localhost:8000/health
```

## 📚 Documentation

### API Documentation

- **OpenAPI**: Auto-generated at `/docs`
- **Redoc**: Alternative docs at `/redoc`

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Run setup script
4. Make changes
5. Run tests
6. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

### Getting Help

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Check docs/ directory

### Common Issues

1. **Docker Connection Issues**: Ensure Docker is running
2. **Database Connection**: Check environment variables
3. **API Key Issues**: Verify LLM provider credentials
4. **Port Conflicts**: Check if ports are available

---

**🌊 Dive deep into oceanographic data with AI-powered insights!**
