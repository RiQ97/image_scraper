from flask import Flask, render_template, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import logging
import pymongo
import os
from dotenv import load_dotenv

logging.basicConfig(filename="scrapper.log", level=logging.INFO)
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            query = request.form['content'].replace(" ", "")
            save_dir = "images/"
            os.makedirs(save_dir, exist_ok=True)

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            response = requests.get(f"https://www.google.com/search?q={query}&tbm=isch", headers=headers)

            soup = BeautifulSoup(response.content, "html.parser")
            img_tags = soup.find_all("img")[1:]  # Skip the first img tag

            img_data = [{"Index": idx, "Image": requests.get(tag['src']).content} for idx, tag in enumerate(img_tags)]
            for idx, data in enumerate(img_data):
                with open(os.path.join(save_dir, f"{query}_{idx}.jpg"), "wb") as f:
                    f.write(data["Image"])

            mongo_uri = os.getenv('MONGO_URI')
            client = pymongo.MongoClient(mongo_uri)
            db = client['image_scrap']
            db['image_scrap_data'].insert_many(img_data)

            return "Images loaded successfully"
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return 'Something went wrong'

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
