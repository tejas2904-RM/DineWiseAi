# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an AI-powered restaurant recommendation system inspired by Zomato.  
The application should combine structured restaurant data with a Large Language Model (LLM) to deliver personalized, human-like suggestions based on user preferences.

## Objective

Design and implement an application that can:

- Accept user preferences such as location, budget, cuisine, and minimum rating.
- Use a real-world restaurant dataset.
- Leverage an LLM to generate personalized recommendations with clear reasoning.
- Present recommendations in a concise and user-friendly format.

## System Workflow

### 1) Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields, including:
  - Restaurant name
  - Location
  - Cuisine
  - Estimated cost
  - Rating

### 2) User Input Collection

Collect the following user preferences:

- Location (for example, Delhi or Bangalore)
- Budget range (low, medium, high)
- Preferred cuisine (for example, Italian or Chinese)
- Minimum acceptable rating
- Additional preferences (for example, family-friendly or quick service)

### 3) Integration Layer

- Filter and prepare dataset entries based on user preferences.
- Convert filtered structured data into an effective LLM prompt.
- Design prompting logic to help the LLM compare, reason, and rank restaurant options.

### 4) Recommendation Engine

Use the LLM to:

- Rank the most relevant restaurants.
- Explain why each recommendation matches the user’s preferences.
- Optionally provide a short summary of trade-offs among top options.

### 5) Output Presentation

Display top recommendations with:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation

The final output should be accurate, easy to understand, and useful for decision-making.
