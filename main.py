from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange, URL
import requests
import os

TMDB_API = "f702aacc24c78407b1652b239b0dcaca"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-data.sqlite-3"
db = SQLAlchemy(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    title = db.Column("Title", db.String(), unique=True, nullable=False)
    year = db.Column("Year", db.String(), nullable=False)
    description = db.Column("Description", db.String(), nullable=False)
    rating = db.Column("Rating", db.Float(), nullable=True)
    ranking = db.Column("Ranking", db.Integer, nullable=True)
    review = db.Column("Review", db.String(), nullable=True)
    movie_link = db.Column("Link", db.String(), nullable=True)
    image = db.Column("Image", db.String(), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'


class MovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")
class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

if not os.path.isfile("sqlite:///movie-data.sqlite-3"):
    db.create_all()


#
# new_movie = Movie(title="Phone Booth",year ="2002",description="Stuart Shepard, a publicist, finds his life under threat when he answers a ringing phone at a phone booth. The caller tells him that he will be shot the minute he cuts the call.",rating=7.1,ranking=10,review="Best thriller I've seen till date.",image="https://m.media-amazon.com/images/M/MV5BMTcxNDQ5MzAyOV5BMl5BanBnXkFtZTYwMjkxMTU3._V1_FMjpg_UX1000_.jpg")
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
    return render_template("index.html", movies=all_movies)





@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        print(title)
        params = {
            "api_key": TMDB_API,
            "language": "en-US",
            "query": title,
            "page": "1",
            "include_adult": "'false"
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params)
        data = response.json()['results']
        return render_template("select.html", data=data)
    return render_template("add.html", form=form)


@app.route('/select')
def select():
    movie_id = request.args.get('id')
    params = {
        "api_key": TMDB_API,
        "language": "en-US"
    }
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params=params)
    data = response.json()

    new_movie = Movie(title=data['original_title'], year=data['release_date'].split("-")[0],
                      description=data['overview'], image=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
                      movie_link=data["homepage"])
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('update',id=new_movie.id))

@app.route("/update", methods=["GET", "POST"])
def update():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    if form.validate_on_submit():
        new_rating = form.rating.data
        new_review = form.review.data
        movie_selected.rating = new_rating
        movie_selected.review = new_review
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie_selected=movie_selected,form=form)

if __name__ == '__main__':
    app.run(debug=True)
