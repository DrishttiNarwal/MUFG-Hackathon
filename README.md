# 🤖 Insurance Bot - AI-Powered Insurance Recommendation System  

##  Overview  
Insurance Bot is an intelligent recommendation system that helps users find the most suitable insurance policies based on their profile and requirements. The system supports multiple insurance types across different countries, leveraging machine learning and natural language processing to provide personalized recommendations with clear explanation. 
It uses a hybrid approach (ML + rule-based) so it stays smart, simple, and works on any kind of data.
And it’s not just a bot — it’s an intelligent, responsible and self-explanatory assistant that makes insurance easy to understand.

---

## 🎥 Final Project Demo Video  

https://github.com/user-attachments/assets/ba9e6967-8dff-4809-8c7b-512180234a7d

##  Features <a name="features"></a>  

### Multi-Country Support  
- **India & Australia Coverage**  
- Region-specific policy recommendations  
- Currency and regulation compliance  

### Insurance Types  
- 🏥 Health Insurance  
- 💖 Life Insurance  
- ✈️ Travel Insurance  
- 🏠 House Insurance  
- 🚗 Vehicle Insurance  

### AI-Powered Features  
- **Smart Recommendations**: ML models trained on extensive insurance data  
- **Natural Language Processing**: Advanced chat interface using LangChain  
- **Real-time Premium Calculation**: Instant cost estimates  
- **Policy Explanation**: AI-generated simple explanations of complex terms  
- **Graph RAG Integration**:  
  - Retrieves knowledge from **40 PDFs** and **2 CSVs (10,000×25 rows each)**  
  - Data divided between India & Australia, aligned with **IRDAI & APRA regulations**  
  - Finds **relationships between user profiles, policies, and regulations**  
  - Ensures contextual and regulation-compliant recommendations  

---

##  Technology Stack <a name="technology-stack"></a>  

### Backend (FastAPI)  
- **Python + FastAPI**: High-performance API backend  
- **scikit-learn**: ML model training and inference  
- **LangChain**: Natural language processing and explanations  
- **ChromaDB**: Vector storage for RAG capabilities  
- **Neo4j**: Knowledge Graph for Graph RAG queries  
- **Pydantic**: Data validation and settings management  

### Frontend (React)  
- **React**: Modern UI framework  
- **Material-UI**: Component library  
- **React Router**: Navigation and routing  
- **Axios**: API integration  

---

##  Architecture <a name="architecture"></a>  

<img width="794" height="980" alt="diagram-export-8-22-2025-12_37_47-PM" src="https://github.com/user-attachments/assets/570bd088-ea15-449c-ac77-29e64f602313" />

## Dataset
https://drive.google.com/drive/folders/1-j18M_fTbyKM5-6jziycuqmet79JUO-E?usp=sharing - – dive into the raw data!

* **Synthetic Data** generated using **current trends + IRDAI (India) & APRA (Australia) regulations**
* **40 PDFs** → Insurance regulatory documents, clauses, and market reports
* **2 CSVs** → \~**10,000×25 rows each**, split between India & Australia
* Used for **model training, Graph RAG retrieval, and PowerBI dashboards**

https://youtu.be/EB1_zJiKx44 – check the visualization out!
  

---

## Scalability

* **Hybrid Architecture** → combines **ML-based predictive modeling** with **rule-based decision checks** for compliance and interpretability
* **Graph RAG with Neo4j** → scales to **millions of relationships**
* **Dockerized Deployment** → scalable across cloud 

---

## Neo4j + Graph RAG

* **Neo4j Graph Database** stores:

  * Policies, premiums, diseases, coverage, add-ons, exclusions, regulations

* **Graph RAG workflow**:

  * CSV/PDF embeddings → stored in ChromaDB
  * Linked into Neo4j graph relationships
  * Queries combine retrieved embeddings + graph reasoning
  * LLM uses this structured context to produce **explainable recommendations**

---

## UI Screenshots

### Landing Page

![WhatsApp Image 2025-08-22 at 14 16 18_7fc28560](https://github.com/user-attachments/assets/ae0cfefd-4560-4cd6-a8c7-1f266c15e09a)


### Country Selection

<<<<<<< HEAD
## Features

- **Insurance Recommendation Engine**
  - Provides personalized policy recommendations across Health, Travel, Property, Vehicle, and Life insurance.
  - Aligns suggestions with member’s lifestyle, financial goals, and life stage.
  - Offers transparent comparison of premiums, benefits, and exclusions.

- **Graph-based Analysis (Neo4j + NetworkX + FAISS)**
  - Visualizes complex relationships between insurance products, clauses, and user preferences.
  - Enables interactive graph node exploration for hidden patterns and connections.
  - Supports similarity search for related policies using FAISS.

- **RAG-powered Q&A (Retrieval-Augmented Generation)**
  - Delivers accurate, context-aware answers to member queries.
  - Ensures traceable responses by citing relevant documents and clauses.
  - Reduces dependency on manual support while maintaining compliance.

- **PowerBI Dashboard**
  - Provides interactive analytics on the insurance dataset.
  - Displays multiple visualizations (premiums, coverage, claims, etc.).
  - Enables real-time filtering and scenario testing (what-if analysis).

- **FastAPI Backend**
  - Modular microservice architecture for recommendation and RAG pipelines.
  - Easy deployment with clean API endpoints.
  - Ensures scalability and integration with frontend or chatbot interfaces.

- **Scalability & Compliance**
  - Designed to handle large datasets and user queries efficiently.
  - Supports compliance checks with transparent audit trails.
  - Reduces support costs by 30–40% through automation.

- **User-Centric Experience**
  - Personalized journey based on member profile and needs.
  - Clear, jargon-free explanations to reduce decision fatigue.
  - Real-time scenario testing to compare outcomes before choosing a policy.

------------------------------------------------------------------------

## Graph-based Exploration

-   **Neo4j Knowledge Graph**: Stores insurance policies, claims, and
    customer relationships.\
-   **NetworkX Integration**: Enables interactive graph traversal and
    visualization.\
-   **FAISS**: Used for semantic similarity search over insurance
    documents and embeddings.\
-   Clicking on nodes reveals **linked policies, risks, and
    recommendations** for deeper insights.

------------------------------------------------------------------------

## Tech Stack

| Category                       | Tools / Models Used                                                                  |
|--------------------------------|--------------------------------------------------------------------------------------|
| **AI Implementation**          | Agentic AI                                                                           |
| **LLM Used**                   | gemini-2.0-flash                                                                     |
| **Frontend**                   | React.js                                                                             |
| **Backend**                    | Python, FastAPI                                                                      |
| **Graph Database**             | Neo4j                                                                                |
| **Vector Search**              | FAISS                                                                                |
| **Embedding Search**           | all-MiniLM-L6-v2, ChromaDB                                                           |
| **Visualization**              | PowerBI, NetworkX                                                                    |
| **ML/DL Models**               | GraphRAG pipeline, Transformers                                                      |
| **Dataset**                    | Generated synthetic + real-world insurance schema                                    |
| **Explored ML Models**         | K-Means, PCA, Linear Regression, Random Forest, CatBoost                             |
| **Accuracy Enhancement**       | GridSearchCV, ANN, Cross Validation                                                  |
=======
![WhatsApp Image 2025-08-22 at 14 16 19_0d3c756a](https://github.com/user-attachments/assets/e70790be-e3e4-47b2-8840-1d627a0e7367)
>>>>>>> 85215b8f90d582ff7d41ae35db91298eb042edcb


### Insurance Type Selection

![WhatsApp Image 2025-08-22 at 14 16 19_9d123212](https://github.com/user-attachments/assets/89f8c71b-9b80-42d2-9994-cd0fe1de0fd4)


### Recommendations Page

![WhatsApp Image 2025-08-22 at 14 16 19_98f81708](https://github.com/user-attachments/assets/f8c7ae6e-8e26-450c-8d8e-5e71e3abf113)


---

## Setup and Installation <a name="setup-and-installation"></a>

### Prerequisites

* Docker and Docker Compose
* Git

### Quick Start

Clone the repository:

```bash
git clone https://github.com/Ishaan2605/Insurance-Bot.git
cd Insurance-Bot
```

Start with Docker Compose:

```bash
docker-compose up --build
```

Access the application:

* Frontend: [http://localhost:80](http://localhost:80)
* Backend API: [http://localhost:8000](http://localhost:8000)
* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Manual Setup (Development)

#### Backend Setup

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\\venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

#### Frontend Setup

```bash
cd mufg-insurance-frontend
npm install
npm start
```

---

## Usage Guide <a name="usage-guide"></a>

1. **Select Country**: Choose between India and Australia
2. **Choose Insurance Type**: Select from Health, Life, Travel, House, or Vehicle insurance
3. **Fill Details**: Provide required information
4. **Get Recommendations**: Receive AI-powered insurance suggestions


---

## API Documentation

### POST /recommend

Get insurance policy recommendations with explanations

**Request Body:**

```json
{
    "country": "india|australia",
    "policy": "health|life|travel|house|vehicle",
    "data": {
        // User profile and requirements data
    }
}
```

**Response:**

```json
{
    "country": "string",
    "policy": "string",
    "recommendation": { },
    "explanations": { }
}
```

---

## Project Structure

```
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── artifacts/             # ML model artifacts
│   ├── india_*/           # India models
│   └── australia_*/       # Australia models
├── scripts/
│   ├── api/               # API utilities
│   ├── llm/               # LLM integration
│   ├── preprocessing/     # Data preprocessing
│   ├── rag/               # RAG implementation
│   └── recommendation/    # ML prediction logic
├── mufg-insurance-frontend/
│   ├── src/               # React source code
│   └── public/            # Static assets
└── vectorstore/           # ChromaDB storage
```

---

## Hackathon Use Cases

* **Personalized Policy Recommendations**: ML + Graph RAG based
* **Explainable AI**: Transparent decision-making
* **Regulation-Aware Analytics**: IRDAI & APRA compliance
* **Dataset Visualization**: PowerBI dashboards for business teams
* **Responsible AI**: Considered Responsible AI features to mitigate bias
---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">  
  Made with ❤️ by Team Insurance Bot  
</p>  
```

