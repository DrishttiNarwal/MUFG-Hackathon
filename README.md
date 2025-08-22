# MUFG-Hackathon

An AI-powered insurance recommendation and analysis system that
integrates **RAG (Retrieval-Augmented Generation)**, **graph-based
insights**, and **PowerBI dashboards** to provide personalized insurance
solutions.

------------------------------------------------------------------------

## Demo

-   Final Project Demo Video
-   PowerBI Dashboard walkthrough (Insurance dataset analytics)\
-   Graph node exploration (interactive insights via Neo4j + NetworkX +
    FAISS)

------------------------------------------------------------------------

## Features

-   **Insurance Recommendation Engine**: Provides policy recommendations
    for Health, Travel, Property, Vehicle, and Life insurance.\
-   **Graph-based Analysis (Neo4j + NetworkX + FAISS)**: Visualize
    relationships and explore insights by clicking on graph nodes.\
-   **RAG-powered Q&A**: Retrieve contextual insurance information with
    natural language queries.\
-   **PowerBI Dashboard**: Interactive dashboard built on generated
    dataset with multiple graphs for detailed analysis.\
-   **FastAPI Backend**: Deployed with modular scripts for
    recommendation and RAG pipeline.

------------------------------------------------------------------------

## PowerBI Dashboard Insights

The dataset generated from our recommendation pipeline was analyzed with
PowerBI:\
- **Travel Insurance**: Seasonal claim trends, risk hotspots, and
customer demographics.\
- **Health Insurance**: Age-based premium analysis, chronic illness
claims, hospital coverage.\
- **Property Insurance**: Claim frequencies across geographies, fraud
detection indicators.\
- **Vehicle Insurance**: Accident patterns, damage categories, and
claim-to-premium ratio.\
- **Life Insurance**: Long-term policy uptake, customer retention, and
premium distribution.

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

-   **Backend**: Python, FastAPI\
-   **Graph DB**: Neo4j\
-   **Vector Search**: FAISS\
-   **Visualization**: PowerBI, NetworkX\
-   **ML/DL Models**: GraphRAG pipeline, Transformers\
-   **Dataset**: Generated synthetic + real-world insurance schema

------------------------------------------------------------------------

## Running the Project

1.  **Clone the repo**

    ``` bash
    git clone <your-repo-link>
    cd Insurance-Bot-main
    ```

2.  **Create virtual environment & install dependencies**

    ``` bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    source venv/bin/activate  # On Mac/Linux
    pip install -r requirements.txt
    ```

3.  **Run Neo4j & test connectivity**

    ``` bash
    python .\scripts\rag\graph_rag.py ping
    ```

4.  **Start the FastAPI app**

    ``` bash
    uvicorn app:app --reload
    ```

------------------------------------------------------------------------

## Contributors

-   Drishtti Narwal
-   Atharv Kulkarni
-   Ishaan Despande
-   Arya Barai

------------------------------------------------------------------------

## Future Work

-   Expand multimodal insurance dataset\
-   Auto update of model with changing policy\
-   Deploy on cloud with CI/CD for scalability