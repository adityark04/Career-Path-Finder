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



## 🚀 Installation & Launch

To get the project running, execute the following commands in your terminal in order:

```bash
# 1. Clone the repository and navigate into it
git clone https://github.com/your-username/pathfinder-project.git
cd pathfinder-project

# 2. Create and activate a Python virtual environment
python -m venv venv
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
# source venv/bin/activate

# 3. Install all necessary packages
python -m pip install -r requirements.txt

# 4. Run the data pipeline to fetch jobs and create AI models
# This part may take a few minutes to complete
python -m scrapers.main_scraper
python generate_embeddings.py

# 5. Launch the Flask web application
python app.py

# 6. Once the server is running, open your browser and go to:
# http://127.0.0.1:5000
