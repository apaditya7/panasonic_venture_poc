# Panasonic Venture POC - Industrial Machine Monitoring System

## Overview

This Proof of Concept (POC) demonstrates an intelligent industrial machine monitoring system that combines IoT sensor data with Large Language Model (LLM) powered insights to revolutionize manufacturing operations. The system transforms raw machine data into actionable, natural language insights that operators can easily understand and act upon.

## Our Solution Approach

### 1. **LLM-Powered Contextual Intelligence**
Instead of just displaying charts and numbers, our system:
- Converts machine sensor data into natural language insights
- Provides contextual explanations: *"The injection molding machine is showing 20% higher pressure than normal, combined with temperature fluctuations. This pattern typically indicates worn seals or blockages."*
- Generates actionable recommendations: *"Schedule maintenance for Machine B within 48 hours based on vibration patterns"*

### 2. **Predictive Narrative Generation**
- **What's happening**: Real-time status interpretation
- **Why it's happening**: Root cause analysis based on patterns
- **What to do next**: Prioritized action items with urgency levels

### 3. **Multi-Modal Data Processing**
- Temperature, vibration, pressure, RPM, and power consumption monitoring
- Pattern recognition across different machine types
- Anomaly detection with severity classification

## Technical Architecture

### Backend (Python FastAPI)
```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # REST API endpoints
│   │   ├── machines.py      # Machine data and status endpoints
│   │   └── insights.py      # LLM-generated insights endpoints
│   ├── services/            # Business logic layer
│   │   ├── anomaly_detector.py    # Statistical analysis & anomaly detection
│   │   ├── llm_service.py         # OpenAI API integration
│   │   └── machine_simulator.py   # Realistic sensor data generation
│   ├── models/              # Data models and schemas
│   │   └── machine.py       # Machine data structures
│   └── core/                # Core utilities and configurations
└── requirements.txt         # Python dependencies
```

**Key Technologies:**
- **FastAPI**: High-performance API framework with automatic documentation
- **OpenAI GPT-4**: Advanced language model for insight generation
- **WebSockets**: Real-time data streaming to frontend
- **Pandas/NumPy**: Statistical analysis and data processing
- **Pydantic**: Data validation and serialization

### Frontend (React.js)
```
frontend/
├── src/
│   ├── App.js               # Main application component
│   ├── components/          # Reusable UI components
│   │   ├── Dashboard.js     # Main monitoring dashboard
│   │   ├── MachineCard.js   # Individual machine status cards
│   │   ├── AlertPanel.js    # Real-time alerts and notifications
│   │   └── InsightsChat.js  # Chat-like LLM insights interface
│   ├── services/            # API communication layer
│   │   ├── api.js           # REST API client
│   │   └── websocket.js     # Real-time data connection
│   └── styles/              # CSS styling
├── public/
└── package.json
```

**Key Technologies:**
- **React 18**: Modern component-based UI framework
- **Chart.js**: Interactive data visualization
- **WebSocket Client**: Real-time data updates
- **Axios**: HTTP client for API communication
- **Responsive Design**: Mobile-friendly interface

## Core Features

### 1. **Real-Time Machine Monitoring**
- Live sensor data visualization
- Multi-machine dashboard view
- Color-coded status indicators (Normal, Warning, Critical)
- Historical trend analysis

### 2. **Intelligent Anomaly Detection**
- Statistical threshold monitoring
- Pattern-based anomaly identification
- Machine learning-enhanced predictions
- Severity classification (Info, Warning, Critical)

### 3. **Natural Language Insights**
- Conversational explanations of machine status
- Predictive maintenance recommendations
- Root cause analysis in plain English
- Contextual understanding of manufacturing processes

### 4. **Alert Management System**
- Priority-based notification system
- Real-time alerts with LLM-generated descriptions
- Mobile-responsive notifications
- Historical alert tracking


### Context-Aware Responses
The system maintains context about:
- Machine relationships and dependencies
- Manufacturing process requirements
- Historical failure patterns
- Maintenance schedules and windows

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env

# Run the server
python app/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access the Application
- Frontend Dashboard: `http://localhost:3000`
- Backend API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`


## Technical Specifications

### Performance Targets
- **Real-time Updates**: < 100ms data refresh rate
- **Alert Response**: < 5 seconds from anomaly detection to notification
- **API Response Time**: < 200ms for standard requests
- **Uptime**: 99.9% availability target

### Security Features
- API key authentication
- CORS protection
- Input validation and sanitization
- Environment variable protection
