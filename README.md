# MUFG-Hackathon - Group No. 18

Superannuation members often struggle to navigate complex insurance options, facing confusing product clauses, opaque premiums, and a lack of personalized guidance. Existing tools rarely provide real-time scenario testing or recommendations tailored to individual life stages and financial goals, leading to decision fatigue. With the global insurance and superannuation market valued in trillions and moving rapidly toward digital adoption, there is a strong need for smarter solutions. Our project addresses this by leveraging AI to deliver personalized, transparent, and traceable insurance advice, reducing support costs, ensuring compliance, and empowering members to make confident and informed choices about their superannuation coverage.

------------------------------------------------------------------------

## Demo

- [Final Project Demo Video](https://youtu.be/pwmYsWL7-uI)
- [PowerBI Dashboard Walkthrough (Insurance Dataset Analytics)](https://youtu.be/EB1_zJiKx44)
- [Graph Node Exploration (Interactive Insights via Neo4j + NetworkX + FAISS)](https://youtu.be/Oh24Uh5J5_E)


------------------------------------------------------------------------

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

| Category                       | Tools / Models Used                                                                 |
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


------------------------------------------------------------------------

## Running the Project

1.  **Clone the repo**

    ``` bash
    git clone <https://github.com/DrishttiNarwal/MUFG-Hackathon>
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

4.  **Start the FastAPI Backend**

    ``` bash
    uvicorn app:app --reload
    ```
5.  **Start the React.js Frontend**
    ``` bash
    npm start
    ```
------------------------------------------------------------------------
## Architecture diagram


------------------------------------------------------------------------

## Contributors

-   Drishtti Narwal
-   Atharv Kulkarni
-   Ishaan Despande
-   Arya Barai

-   (Final Year AI & ML Students at SIT, Pune. Batch 2022-26)
------------------------------------------------------------------------

## Future Work

-   Expand multimodal insurance dataset\
-   Auto update of model with changing policy\
-   Deploy on cloud with CI/CD for scalability