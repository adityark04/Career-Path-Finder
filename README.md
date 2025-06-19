# Career Path Finder
Using DL and ML concepts to showcase Career options based on known skills

#  Pathfinder 🚀 - AI-Powered Career Roadmap Generator

  <!-- TODO: Replace this with a real screenshot of your app! -->

Pathfinder is an intelligent web application designed to help students and aspiring professionals navigate the complexities of choosing a career path. Instead of just matching keywords, Pathfinder uses Deep Learning to understand the user's skills and interests, recommends relevant job opportunities scraped live from across the web, and generates a personalized learning roadmap with high-quality courses and tutorials.

This project was built from scratch as a practical application of Natural Language Processing (NLP), web scraping, and modern web development practices.

---

## ✨ Features

-   **AI-Powered Semantic Search:** Utilizes `sentence-transformers` to understand the *meaning* behind a user's query, providing much more relevant job recommendations than simple keyword matching.
-   **Multi-Source Job Aggregation:** Scrapes and aggregates entry-level job postings from sources like LinkedIn, providing a rich and diverse dataset.
-   **Dynamic Learning Roadmap:** For the top job recommendation, Pathfinder performs a live search on YouTube and Coursera to find relevant, up-to-the-minute learning resources.
-   **Hybrid Recommendation System:** Combines live-scraped learning resources with a high-quality, pre-defined database of courses to ensure a robust and reliable user experience.
-   **Modern & Responsive UI:** Clean, professional, and mobile-friendly interface built with Bootstrap.

---

## 🛠️ Technology Stack

-   **Backend:** Python, Flask
-   **Deep Learning / AI:** PyTorch, `sentence-transformers` (for creating text embeddings)
-   **Web Scraping:** `requests`, `BeautifulSoup4`, `selenium` (for dynamic sites)
-   **Data Handling:** `pandas`, `NumPy`
-   **Frontend:** HTML5, CSS3, Bootstrap 5
-   **Concurrency:** `concurrent.futures` for parallel live scraping.

---

## 🚀 How to Run Locally

Follow these steps to set up and run the project on your local machine.


### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pathfinder-project.git
cd pathfinder-project

### 2. Set Up a Virtual Environment

python -m venv venv
# Activate it
# On Windows:
venv\Scripts\

### 3. Install Dependencies
python -m pip install -r requirements.txt

### 4. Run the Data Pipeline
python -m scrapers.main_scraper
python generate_embeddings.py

### 5. Run the App
python app.py

### 6. Open the http link in the terminal on the browser
