from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get Reddit credentials from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT = os.getenv('USER_AGENT')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

# Define subreddit categories
CATEGORIES = {
    'Technology': ['technology', 'Futurology', 'Android', 'Apple', 'gadgets', 'technews'],
    'Science': ['science', 'space', 'physics', 'biology', 'chemistry', 'astronomy', 'earthscience'],
    'AI': ['ArtificialIntelligence', 'MachineLearning', 'deepdreams', 'AI', 'learnmachinelearning'],
    'Space': ['space', 'astronomy', 'NASA', 'exoplanets', 'Astrophysics'],
    'Memes': ['memes', 'dankmemes', 'memes_irl', 'me_irl', 'funny'],
    'Art': ['art', 'Illustration', 'ArtHistory', 'digitalart', 'artstation'],
    'Gaming': ['gaming', 'pcgaming', 'gamers', 'nintendo', 'xbox', 'playstation'],
    'Nature': ['natureisfuckinglit', 'outdoors', 'wildlifephotography', 'naturephotography'],
    'History': ['history', 'worldhistory', 'AskHistorians', 'HistoryMemes'],
    'News': ['news', 'worldnews', 'politics', 'business', 'sports']
}

# Get Reddit access token
def get_access_token():
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        'grant_type': 'password',
        'username': REDDIT_USERNAME,
        'password': REDDIT_PASSWORD
    }
    headers = {'User-Agent': USER_AGENT}

    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=auth, data=data, headers=headers)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("Error getting access token:", response.status_code, response.text)
        return None

# Fetch top posts from a subreddit
def get_top_posts(subreddit):
    token = get_access_token()
    if token is None:
        return []

    headers = {
        'Authorization': f'bearer {token}',
        'User-Agent': USER_AGENT
    }

    url = f"https://oauth.reddit.com/r/{subreddit}/top/.json?limit=5&t=week"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = []
        for post in data['data']['children']:
            post_data = post['data']
            posts.append({
                'title': post_data.get('title'),
                'score': post_data.get('score'),
                'comments': post_data.get('num_comments'),
                'url': f"https://reddit.com{post_data.get('permalink')}"
            })
        return posts

    except Exception as e:
        print("Error fetching subreddit posts:", str(e))
        return []

# Home route
@app.route("/", methods=["GET"])
def index():
    selected_category = request.args.get("category")
    selected_subreddit = request.args.get("subreddit")
    posts = []

    if selected_subreddit:
        posts = get_top_posts(selected_subreddit)

    return render_template("main.html",
                           categories=CATEGORIES,
                           selected_category=selected_category,
                           selected_subreddit=selected_subreddit,
                           posts=posts)

# Optional API handler for frontend JavaScript or external use
@app.route("/api/handler", methods=["GET", "POST"])
def api_handler():
    if request.method == "GET":
        return jsonify({"message": "API handler active!"})

    if request.method == "POST":
        data = request.get_json()
        selected_category = data.get("category")
        selected_subreddit = data.get("subreddit")

        posts = get_top_posts(selected_subreddit) if selected_subreddit else []

        return jsonify({
            "posts": posts,
            "category": selected_category,
            "subreddit": selected_subreddit
        })

if __name__ == "__main__":
    app.run(debug=True)
