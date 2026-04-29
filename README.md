# GrowEngine 🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

**[中文文档](README_CN.md)**

GrowEngine is a comprehensive advertising automation platform evolved to include a **Hybrid Recommendation System**. It combines a robust ad campaign management dashboard with an experimental, high-performance recommendation engine integrated from SparrowRecSys.

## ✨ Features

### 🏢 Core Platform
- **📊 Real-time Dashboard**: Monitor Spend, GMV, ROI, and core metrics instantly.
- **📋 Campaign Management**: Full lifecycle management for ad plans (Create, Edit, Pause/Resume).
- **🤖 Smart Diagnosis**: AI-driven optimization suggestions for ad performance.
- **🎮 Bidding Simulation**: Simulate bidding strategies based on OnlineLp algorithms.

### 🎯 Hybrid Recommendation System (New)
Integrated directly with **SparrowRecSys**, offering a "Hybrid Mode" architecture:
- **Python Backend**: Handles Data Management, Feature Engineering, and Click Collection.
- **Model Inference**: Supports Java RecSysServer or TensorFlow Serving for NeuralCF, DeepFM, and DIN models.
- **Interactive UI**: Dedicated React frontend for visualizing recommendations and tracking user interactions.

## 🏗 Architecture

GrowEngine now operates on a modular architecture:

```mermaid
graph TD
    User["User/Visitor"]
    
    subgraph "Ad Management"
        AdminUI["Admin Dashboard"]
        CoreAPI["Core API (8000)"]
    end
    
    subgraph "Recommendation Engine"
        RecUI["RecSys UI"]
        RecAPI["RecSys API (8001)"]
        JavaServ["Java RecSysServer (6010)"]
    end
    
    User --> AdminUI
    User --> RecUI
    
    AdminUI --> CoreAPI
    RecUI --> RecAPI
    
    RecAPI --> JavaServ
    RecAPI -- "Click Logs" --> Data[("CSV/Clicks")]
    Data -- "Training" --> Train[Model Pipeline]
    Train --> JavaServ
```

## 📁 Project Structure

```bash
ProtoAd/
├── frontend/          # Admin Dashboard (React + Vite + TailwindCSS)
├── backend/           # Core Ad Management API (FastAPI)
├── ad_rec_frontend/   # Recommendation System Showcase UI (React)
├── ad_rec_backend/    # RecSys API, Click Collection & Data Mgr
├── SparrowRecSys/     # Original Java Recommendation Engine Source
├── web_visualization/ # Helper visualizations
├── scripts/           # DevOps and utility scripts
└── docker-compose.yml # Full stack orchestration
```

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+
- **Python** 3.10+
- **Docker** (Optional, for full stack deployment)

### 💻 Local Development

Start all four development services with one command:

```bash
./scripts/start-dev.sh
```

The script installs Python and Node dependencies as needed, reuses
`$HOME/venv/huzhe` by default, and starts:

| Service | URL |
|---------|-----|
| Core Frontend | `http://localhost:5173/adproto/` |
| Core API | `http://localhost:8000/docs` |
| RecSys Frontend | `http://localhost:5174` |
| RecSys API | `http://localhost:8001/docs` |

To use a different Python virtual environment path:

```bash
VENV_DIR=.venv ./scripts/start-dev.sh
```

## 🐳 Docker Deployment

Run the entire suite with one command:

```bash
docker compose up -d --build
```
This will start:
- Core Backend: `http://localhost:8000`
- Core Frontend: `http://localhost:3000/adproto/`
- RecSys Backend: `http://localhost:8001`
- RecSys Frontend: `http://localhost:3001`

## 📡 API Documentation

| Service | Base URL | Documentation |
|---------|----------|---------------|
| **Core API** | `http://localhost:8000` | `/docs` |
| **RecSys API** | `http://localhost:8001` | `/docs` |

### Key RecSys Endpoints
- `GET /api/rec/ads`: Get personalized ad recommendations.
- `GET /api/rec/similar`: Get similar items (Item2Vec).
- `POST /api/rec/click`: Log user interaction events.
- `POST /api/rec/train`: Trigger model retraining pipeline.

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=huzhe01/adproto&type=Date)](https://star-history.com/#huzhe01/adproto&Date)

## 🤝 Contributing

We welcome contributions!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
