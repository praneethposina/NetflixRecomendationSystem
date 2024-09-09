# app.py
from flask import Flask, render_template, send_from_directory, request, jsonify
from joblib import load
from joblib import load
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas
import csv

app = Flask(__name__)

with open("data.pickle", "rb") as f:
    data = pickle.load(f)
f.close()

model = load('model.joblib')
scaler = StandardScaler()
movie_features = data.drop(columns=['title'])
movie_features_scaled = scaler.fit_transform(movie_features)
data['cluster'] = model.labels_
def birch_method_movies(movie_name, data, model, scaler, top_n=3):
    movie_name = movie_name.lower()
    matching_movies = data[data['title'].str.lower() == movie_name]
    if matching_movies.empty:
        return "No such movie found"
    movie_index = matching_movies.index[0]
    movie_features = data.drop(columns=['title', 'cluster']).iloc[movie_index].values.reshape(1, -1)
    movie_features_scaled = scaler.transform(movie_features)
    predicted_cluster = model.labels_[movie_index]
    cluster_movies = data[data['cluster'] == predicted_cluster]
    similarities = cosine_similarity(movie_features_scaled, scaler.transform(cluster_movies.drop(columns=['title', 'cluster'])))
    similar_movie_indices = similarities.argsort()[0][-top_n-1:-1][::-1]
    similar_movies = cluster_movies.iloc[similar_movie_indices]['title'].tolist()
    return similar_movies

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eda')
def eda():
    images = ['Assets/1.png', 'Assets/2.png', 'Assets/3.png', 'Assets/4.png', 'Assets/5.png', 'Assets/6.png', 'Assets/7.png', 'Assets/8.png', 'Assets/9.png', 'Assets/10.png']
    return render_template('EDA.html', images=images)

@app.route('/movies.csv')
def serve_csv():
    return send_from_directory(app.root_path, 'movies.csv')

@app.route('/results', methods=('POST', 'GET'))
def result():
    if request.method == 'GET':
        movie = request.args.get('movie').lower()
        pred_mov = birch_method_movies(movie, data, model, scaler, top_n=5)
        if isinstance(pred_mov, str):
            return render_template('result.html', error=pred_mov, org = movie)
        else:
            movie_details = []
            pred_mov = [title.lower() for title in pred_mov]
            with open('movies.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['title'].lower() in pred_mov:
                        movie_details.append({
                            'title': row['title'],
                            'type': row['type'],
                            'date_added': row['date_added'],
                            'release_year': row['release_year'],
                            'rating': row['rating'],
                            'description': row['description']
                        })
            return render_template('result.html', movies=movie_details, org = movie.upper())

@app.route('/image/<int:image_index>')
def full_screen(image_index):
    image_url = 'Assets/{}.png'.format(image_index)
    return render_template('full_screen.html', image=image_url)

if __name__ == '__main__':
    app.run(debug=True)