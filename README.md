

Readme · MD
Movie Library
A small movie search and favorites app built with Python and Flask. It uses the OMDb API for movie data and keeps your favorites in a local JSON file.

I started it as a command-line script (main.py) and later put a web interface on top of it (app.py). Both use the same MovieLibrary class, so the CLI and the website share the same favorites.

What it does
Search by exact title or by keyword
Open a movie page with poster, genres, plot, director, actors and IMDb rating
Save movies to a favorites list and remove them again
Favorites are sorted by IMDb rating, highest first
Error messages when the API fails, the internet is down or nothing is found
Setup
You need Python 3.9+ and a free OMDb API key (you can get one at https://www.omdbapi.com/apikey.aspx).

bash
git clone <repo-url>
cd <project-folder>

python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install flask requests python-dotenv
Create a .env file in the project root:

OMDB_API_KEY=your_key_here
FLASK_SECRET_KEY=any_random_string
FLASK_SECRET_KEY is optional. If you leave it out, a random one is generated on every start, which only means flash messages won't survive a restart.

Running it
Web version:

bash
python app.py
Then open http://127.0.0.1:5000 in your browser.

Terminal version:

bash
python main.py
Project structure
main.py          MovieLibrary class + the terminal menu
app.py           Flask routes
templates/
  base.html      layout, navigation, flash messages
  index.html     search page
  results.html   keyword search results
  movie.html     movie details
  favorites.html favorites list
  _macros.html   poster macro (with a fallback when there is no poster)
static/
  style.css
favorite_movies.json   created automatically on first save
The HTML files go in a templates/ folder and style.css in static/, which is where Flask looks for them by default.

Notes and limitations
Favorites are stored in one JSON file, so there are no user accounts. Everyone who opens the app sees the same list.
OMDb's free plan has a daily request limit, so if searches suddenly stop working, that's probably why.
Keyword search returns only the first page of results (10 movies) from OMDb.
The app runs with debug=True, which is fine for local use but should not be used when deploying it.
Possible next steps
Pagination for search results
Per-user favorites
Filtering favorites by genre
Credits
Movie data and posters come from OMDb.


Claude finished the response
