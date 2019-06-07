from flask import Flask, render_template, request
from sklearn.externals import joblib
import os
import pandas as pd

app = Flask(__name__, static_url_path='/static/')


@app.route('/')
def form():
    return render_template('index.html')


@app.route('/predict_price', methods=['POST', 'GET'])
def predict_price():
    # get the parameters
    prod_company = request.form['prod_company']
    collection = request.form['collection']
    year = int(request.form['year'])
    budget = float(request.form['budget'])
    genre_1 = request.form['genre_1']
    genre_2 = request.form['genre_2']
    genre_3 = request.form['genre_3']
    actor_1 = request.form['actor_1']
    actor_2 = request.form['actor_2']
    actor_3 = request.form['actor_3']

    # form a list of income features
    features = []
    features.append(budget)
    features.append(year)

    #get belongs_to_col and collection vote from external dataframe
    if collection == '':
        belongs_to_col = 0
        features.append(belongs_to_col)
        coll_vote = 0
        features.append(coll_vote)
    else:
        belongs_to_col = 1
        features.append(belongs_to_col)
        df_col = pd.read_csv('data/collections.csv')
        for i in df_col.index:
            if df_col.loc[i,'name'] == collection:
                coll_vote = df_col.loc[i,'vote_count']
        features.append(coll_vote)

    # add the genres
    genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Foreign", "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]
    for g in genres:
        if (g == genre_1) | (g == genre_2) | (g == genre_3):
            features.append(1)
        else:
            features.append(0)
    
    # add genres numeric values
    df_genres = pd.read_csv('data/genres.csv')
    g_p = 0
    g_v = 0
    g_r = 0
    for g in genres:
        if (g == genre_1) | (g == genre_2) | (g == genre_3):
            for idx in df_genres.index:
                if df_genres.loc[idx,'name'] == g:
                    g_p = g_p + df_genres.loc[idx,'vote_count']
                    g_v = g_v + df_genres.loc[idx,'vote_average']
                    g_r = g_r + df_genres.loc[idx,'revenue']

    features.append(g_p)
    features.append(g_v)
    features.append(g_r)

    # add production companies
    prod = ["1492 Pictures", "21 Laps Entertainment", "Alcon Entertainment", "Amblin Entertainment", "Anonymous Content", "Apatow Productions", "BBC Films", "Bad Robot", "Big Screen Productions", "Blumhouse Productions", "Canal+", "Castle Rock Entertainment", "Columbia Pictures", "Columbia Pictures Corporation", "DC Comics", "Davis Entertainment", "Dentsu", "Di Bonaventura Pictures", "Dimension Films", "Donners' Company", "Double Feature Films", "DreamWorks Animation", "DreamWorks SKG", "Dune Entertainment", "Dune Entertainment III", "Emmett/Furla Films", "Endgame Entertainment", "Epsilon Motion Pictures", "Escape Artists", "EuropaCorp", "Film4", "FilmNation Entertainment", "Focus Features", "Fox 2000 Pictures", "Fox Searchlight Pictures", "Franchise Pictures", "GK Films", "Happy Madison Productions", "IM Global", "Imagenation Abu Dhabi FZ", "Imagine Entertainment", "Ingenious Film Partners", "Ingenious Media", "Intermedia Films", "Jerry Bruckheimer Films", "Kennedy/Marshall Company, The", "LStar Capital", "Lakeshore Entertainment", "Legendary Pictures", "Lions Gate Films", "Lionsgate", "MTV Films", "Mad Chance", "Malpaso Productions", "Mandate Pictures", "Marc Platt Productions", "Marvel Enterprises", "Marvel Studios", "Metro-Goldwyn-Mayer (MGM)", "Millennium Films", "Miramax Films", "Morgan Creek Productions", "NPV Entertainment", "New Line Cinema", "New Regency Pictures", "Nickelodeon Movies", "Nu Image Films", "Original Film", "Overbrook Entertainment", "Paramount Pictures", "Participant Media", "Pixar Animation Studios", "Plan B Entertainment", "Platinum Dunes", "RatPac-Dune Entertainment", "Regency Enterprises", "Relativity Media", "Revolution Studios", "Revolution Sun Studios", "Saturn Films", "Scott Free Productions", "Scott Rudin Productions", "Screen Gems", "Silver Pictures", "Spyglass Entertainment", "Studio Babelsberg", "StudioCanal", "Summit Entertainment", "TSG Entertainment", "The Weinstein Company", "Touchstone Pictures", "TriStar Pictures", "Twentieth Century Fox Film Corporation", "Universal Pictures", "Vertigo Entertainment", "Village Roadshow Pictures", "Walden Media", "Walt Disney Pictures", "Warner Bros.", "Working Title Films"]
    for p in prod:
        if (p == prod_company):
            features.append(1)
        else:
            features.append(0)

    # add production companies numeric values
    df_prod = pd.read_csv('data/prod_companies.csv')
    p_p = 0
    p_v = 0
    p_r = 0
    for idx in df_prod.index:
        if df_prod.loc[idx,'name'] == prod_company:
            p_p = df_prod.loc[idx,'vote_count']
            p_v = df_prod.loc[idx,'vote_average']
            p_r = df_prod.loc[idx,'revenue']
    features.append(p_p)
    features.append(p_v)
    features.append(p_r)
    
    # add actors
    actors = ["Aaron Eckhart", "Adam Sandler", "Alan Tudyk", "Alec Baldwin", "Amy Adams", "Angelina Jolie", "Anne Hathaway", "Anthony Mackie", "Ben Affleck", "Ben Kingsley", "Ben Stiller", "Bill Hader", "Bill Murray", "Bill Nighy", "Brad Pitt", "Bradley Cooper", "Brendan Gleeson", "Brian Cox", "Bruce McGill", "Bruce Willis", "Cameron Diaz", "Cate Blanchett", "Channing Tatum", "Charlize Theron", "Chris Evans", "Christian Bale", "Ciarán Hinds", "Colin Farrell", "David Koechner", "Dennis Quaid", "Drew Barrymore", "Dwayne Johnson", "Ed Harris", "Elizabeth Banks", "Ewan McGregor", "George Clooney", "Gerard Butler", "Hugh Jackman", "Idris Elba", "J.K. Simmons", "Jack Black", "James Franco", "James Marsden", "Jason Bateman", "Jason Statham", "Jennifer Aniston", "Jeremy Renner", "John C. Reilly", "John Goodman", "John Leguizamo", "Johnny Depp", "Jonah Hill", "Joseph Gordon-Levitt", "Josh Brolin", "Judy Greer", "Julia Roberts", "Julianne Moore", "Justin Long", "Keith David", "Ken Jeong", "Kevin Hart", "Kristen Stewart", "Kristen Wiig", "Liam Neeson", "Luis Guzmán", "Maggie Gyllenhaal", "Mark Ruffalo", "Mark Wahlberg", "Matt Damon", "Matthew McConaughey", "Meryl Streep", "Michael Caine", "Michael Peña", "Michael Shannon", "Michael Sheen", "Morgan Freeman", "Naomi Watts", "Nicolas Cage", "Octavia Spencer", "Owen Wilson", "Paul Bettany", "Paul Giamatti", "Paul Rudd", "Peter Sarsgaard", "Richard Jenkins", "Robert De Niro", "Robert Downey Jr.", "Ron Perlman", "Ryan Reynolds", "Sam Rockwell", "Samuel L. Jackson", "Scarlett Johansson", "Seth Rogen", "Sigourney Weaver", "Stan Lee", "Stanley Tucci", "Stephen Root", "Steve Buscemi", "Steve Carell", "Susan Sarandon", "Terrence Howard", "Tom Hanks", "Tom Wilkinson", "Vince Vaughn", "Viola Davis", "Will Ferrell", "Willem Dafoe", "Woody Harrelson"]
    for a in actors:
        if (a == actor_1) | (a == actor_2) | (a == actor_3):
            features.append(1)
        else:
            features.append(0)

    # add actors numeric values
    df_act = pd.read_csv('data/actors.csv')
    a_p = 0
    a_v = 0
    a_r = 0
    for a in actors:
        if (a == actor_1) | (a == actor_2) | (a == actor_3):
            for idx in df_act.index:
                if df_act.loc[idx,'name'] == a:
                    a_p = a_p + df_act.loc[idx,'vote_count']
                    a_v = a_v + df_act.loc[idx,'vote_average']
                    a_r = a_r + df_act.loc[idx,'revenue']

    features.append(a_p)
    features.append(a_v)
    features.append(a_r)

    # double checking the number of features
    num_features = len(features)

    # load the model and predict
    model = joblib.load('model/model.joblib') # model/linear_regression.pkl
    prediction = model.predict([features])
    predicted_price = prediction.round(1)[0]

    return render_template('results.html',
                            prod_company = prod_company,
                            collection = collection,
                            year = year,
                            budget = "{:,}".format(budget),
                            genre_1 = str(genre_1)+',' if genre_2 else str(genre_1),
                            genre_2 = str(genre_2)+',' if genre_3 else str(genre_2),
                            genre_3 = genre_3,
                            actor_1 = str(actor_1)+',' if actor_2 else str(actor_1),
                            actor_2 = str(actor_2)+',' if actor_3 else str(actor_2),
                            actor_3 = actor_3,
                            num_features = num_features,
                            predicted_price="{:,}".format(predicted_price)
                           )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
