# Project Context: AI-Powered Restaurant Recommendation System

## Overview

This project is an **AI-powered restaurant recommendation service** inspired by **Zomato**. The system intelligently suggests restaurants based on user preferences by combining **structured restaurant data** with a **Large Language Model (LLM)** to produce personalized, human-like recommendations.

---

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world dataset of restaurants
3. Leverages an LLM to generate personalized, human-like recommendations
4. Displays clear and useful results to the user

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the **Zomato dataset** from Hugging Face:
  - **Dataset URL:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
- Extract relevant fields, including:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - Other applicable metadata from the dataset

### 2. User Input

Collect user preferences through the application:

| Preference | Examples / Notes |
|------------|------------------|
| **Location** | Delhi, Bangalore, etc. |
| **Budget** | Low, medium, high |
| **Cuisine** | Italian, Chinese, etc. |
| **Minimum rating** | User-defined threshold |
| **Additional preferences** | Family-friendly, quick service, etc. |

### 3. Integration Layer

The integration layer connects structured data with the LLM:

1. **Filter** restaurant data based on user input
2. **Prepare** a structured subset of relevant restaurants for the LLM
3. **Design a prompt** that enables the LLM to reason over the filtered data and rank options effectively

### 4. Recommendation Engine

Use the LLM to:

- **Rank** restaurants according to how well they match user preferences
- **Explain** why each recommendation fits the user’s criteria
- **Optionally summarize** the overall set of choices (e.g., a brief overview of top picks)

### 5. Output Display

Present the **top recommendations** in a user-friendly format. Each result should include:

- **Restaurant name**
- **Cuisine**
- **Rating**
- **Estimated cost**
- **AI-generated explanation** (why this restaurant was recommended)

---

## High-Level Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  User Input │ ──► │ Integration Layer │ ──► │ Recommendation  │
│ (preferences)│     │ (filter + prompt) │     │ Engine (LLM)    │
└─────────────┘     └──────────────────┘     └─────────────────┘
                              ▲                        │
                              │                        ▼
                    ┌──────────────────┐     ┌─────────────────┐
                    │  Zomato Dataset  │     │ Output Display  │
                    │  (Hugging Face)  │     │ (ranked results)│
                    └──────────────────┘     └─────────────────┘
```

---

## Key Design Principles

- **Hybrid approach:** Combine deterministic filtering (structured data) with LLM reasoning (ranking and explanations).
- **Transparency:** Every recommendation should include an explanation, not just a list of names.
- **Real data:** Recommendations must be grounded in the actual Zomato dataset, not invented restaurants.
- **Usability:** Output must be clear, scannable, and actionable for end users.

---

## Data Source

| Item | Detail |
|------|--------|
| **Source** | Hugging Face |
| **Dataset** | `ManikaSaini/zomato-restaurant-recommendation` |
| **Link** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |

---

## Expected User-Facing Output (Per Recommendation)

```
Restaurant Name: [name]
Cuisine:         [cuisine type(s)]
Rating:          [numeric or star rating]
Estimated Cost:  [cost for two / price range]
Explanation:     [LLM-generated reason this matches the user's preferences]
```

---

## Scope Summary

| Component | Responsibility |
|-----------|----------------|
| **Data ingestion** | Load, clean, and index restaurant records from Hugging Face |
| **User input** | Capture location, budget, cuisine, min rating, and free-form preferences |
| **Integration layer** | Filter dataset → build LLM prompt with structured context |
| **Recommendation engine** | LLM ranks options and writes explanations |
| **Output display** | Render top N recommendations with all required fields |

---

## Reference

The canonical problem definition lives in `docs/problemstatement.txt`.
