import os

from flask import Flask, flash, redirect, render_template, request, url_for

from main import API_KEY, MovieLibrary

app = Flask(__name__)
# Needed for flash messages. Set FLASK_SECRET_KEY in .env to keep it stable
# between restarts; otherwise a random one is generated on each start.
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24).hex()

library = MovieLibrary(API_KEY)


def rating_value(movie):
    try:
        return float(movie.get("rating"))
    except (TypeError, ValueError):
        return 0.0


def is_favorite(imdb_id):
    return any(fav["imdbID"] == imdb_id for fav in library.favorites)


@app.context_processor
def inject_globals():
    return {"favorites_count": len(library.favorites)}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/search")
def search():
    query = request.args.get("q", "").strip()
    mode = request.args.get("mode", "keyword")

    if not query:
        flash("Enter a title or keyword to search.", "error")
        return redirect(url_for("index"))

    if mode == "title":
        movie = library.search_by_title(query)
        if movie:
            return render_template(
                "movie.html", movie=movie, saved=is_favorite(movie["imdbID"])
            )
        return render_template(
            "results.html", query=query, mode=mode, movies=[], error=library.last_error
        )

    movies = library.search_by_keyword(query)
    return render_template(
        "results.html", query=query, mode="keyword", movies=movies, error=library.last_error
    )


@app.get("/movie/<imdb_id>")
def movie_detail(imdb_id):
    movie = library.search_by_id(imdb_id)
    if not movie:
        flash(library.last_error or "Movie not found.", "error")
        return redirect(url_for("index"))
    return render_template("movie.html", movie=movie, saved=is_favorite(imdb_id))


@app.get("/favorites")
def favorites_page():
    movies = sorted(library.favorites, key=rating_value, reverse=True)
    return render_template("favorites.html", movies=movies)


@app.post("/favorites/add")
def add_favorite():
    imdb_id = request.form.get("imdb_id", "").strip()
    movie = library.search_by_id(imdb_id)
    if not movie:
        flash(library.last_error or "Movie not found.", "error")
        return redirect(url_for("index"))

    if library.add_to_favorites(movie):
        flash(f"Saved “{movie.get('Title')}” to favorites.", "success")
    else:
        flash(f"“{movie.get('Title')}” is already in your favorites.", "info")
    return redirect(url_for("movie_detail", imdb_id=imdb_id))


@app.post("/favorites/remove")
def remove_favorite():
    imdb_id = request.form.get("imdb_id", "").strip()
    removed = library.remove_by_id(imdb_id)
    if removed:
        flash(f"Removed “{removed['title']}” from favorites.", "success")
    else:
        flash("That movie is not in your favorites.", "error")
    return redirect(url_for("favorites_page"))


if __name__ == "__main__":
    app.run(debug=True)
