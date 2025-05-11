from flask import Flask, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
CURRENTAPI_KEY = os.getenv("CURRENTAPI_KEY")

def format_time(timestamp):
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except:
        return timestamp

def fetch_from_newsapi():
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"category=technology&language=en&pageSize=10&apiKey={NEWSAPI_KEY}"
    )
    res = requests.get(url)
    data = res.json()

    if data.get("status") != "ok":
        raise Exception("NewsAPI failed")

    articles = []
    for article in data["articles"]:
        articles.append({
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "source": article["source"]["name"],
            "publishedAt": format_time(article["publishedAt"]),
        })
    return articles

def fetch_from_currentapi():
    url = (
        f"https://api.currentsapi.services/v1/latest-news?"
        f"language=en&category=technology&apiKey={CURRENTAPI_KEY}"
    )
    res = requests.get(url)
    data = res.json()

    if data.get("status") != "ok":
        raise Exception("CurrentAPI failed")

    articles = []
    for article in data["news"]:
        articles.append({
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "source": article.get("author", "CurrentAPI"),
            "publishedAt": format_time(article["published"]),
        })
    return articles

def fetch_tech_news():
    try:
        return fetch_from_newsapi()
    except:
        try:
            return fetch_from_currentapi()
        except:
            return []

@app.route("/")
def home():
    articles = fetch_tech_news()
    return jsonify(articles)

# Vercel compatibility
def handler(request, context):
    return app(request.environ, start_response=context.start_response)

