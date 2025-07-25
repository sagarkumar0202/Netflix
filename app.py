from flask import Flask, render_template, request, redirect, session
import sqlite3
import pickle


app = Flask(__name__)
app.secret_key = 'secret123'


# Load ML model files
movies = pickle.load(open('pkl/movies.pkl', 'rb'))
similarity = pickle.load(open('pkl/similarity.pkl', 'rb'))


# SQLite DB connection
def get_db():
    return sqlite3.connect('database/users.db')


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/', methods=['POST'])
def do_login():
    email = request.form['email']
    password = request.form['password']


    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()


    if user:
        session['user'] = email
        return redirect('/home')
    else:
        return render_template("login.html", error="Invalid Credentials")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            return render_template("signup.html", error="User already exists")
       
        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return redirect('/')
   
    return render_template("signup.html")
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            return render_template("forgot.html", error="User already exists")
       
        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return redirect('/')
   
    return render_template("forgot.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/')

    recommendations = []
    selected_movie = ""

    if request.method == 'POST':
        selected_movie = request.form['movie']
        if selected_movie in movies['title'].values:
            idx = movies[movies['title'] == selected_movie].index[0]
            distances = list(enumerate(similarity[idx]))
            movies_list = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]
            for i in movies_list:
                movie_info = movies.iloc[i[0]]
                recommendations.append({
                    'title': movie_info.title,
                    'genre': movie_info.genre,
                    'language': movie_info.language,
                    'rating': movie_info.rating,
                    'image': movie_info.image_file
                })

    trending_df = movies[movies['rating'] > 9]
    trending = trending_df['title'].tolist()

    return render_template("home.html",
                           username=session['user'],
                           movie_list=movies['title'].values,
                           recommended=recommendations,
                           trending=trending,
                           selected_movie=selected_movie)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/visualize')
def visualize():
    import pandas as pd
    import matplotlib.pyplot as plt
    import io
    import base64

    df = pickle.load(open('pkl/movies.pkl', 'rb'))

    # PIE: Language Distribution
    lang_counts = df['language'].value_counts()

    # BAR: Genres with Avg Rating > 9
    genre_high_rating = df.groupby('genre')['rating'].mean()
    genre_high_rating = genre_high_rating[genre_high_rating > 9]

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Pie Chart
    axs[0].pie(lang_counts, labels=lang_counts.index, autopct='%1.1f%%', startangle=90)
    axs[0].set_title('Language Distribution')

    # Bar Chart
    genre_high_rating.plot(kind='bar', color='orange', ax=axs[1])
    axs[1].set_title('Genres with Avg Rating > 9')
    axs[1].set_ylabel('Average Rating')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template("visualize.html", plot=image_base64)

@app.route('/admin')
def admin():
    if 'user' not in session or session['user'] != 'admin':
        return redirect('/')
    movie_data = movies[['title', 'genre', 'language', 'rating']].sort_values(by='rating', ascending=False)
    return render_template('admin.html', movies=movie_data.to_dict(orient='records'))

import pandas as pd

movie_links = pd.read_csv('dataset/movie_links.csv')

@app.route('/watch/<movie>')
def watch(movie):
    link_row = movie_links[movie_links['movie_name'].str.lower() == movie.lower()]
    if not link_row.empty:
        link = link_row.iloc[0]['link']
        return render_template("watch.html", movie=movie, link=link)
    else:
        return "Link not found", 404


@app.route('/subscriptions')
def subscriptions():
    return render_template("subscriptions.html")

@app.route('/payment_success', methods=['POST'])
def payment_success():
    plan = request.form['plan']
    return render_template("payment_success.html", plan=plan)



@app.route('/forgot_password')
def forgot_password():
    return render_template("forgot_password.html")

if __name__ == '__main__':
    app.run(debug=True)
