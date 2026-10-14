import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
FAVORITES_FILE = "favorite_movies.json"
API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = "https://www.omdbapi.com/"


class MovieLibrary:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key was not found!")
        self.api_key = api_key
        self.favorites = self.load_favorites()
        self.last_error = None  # lets the web UI show why a request failed

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
            except:
                return []
        return []

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
            json.dump(self.favorites, file, ensure_ascii=False, indent=2)

    def send_api_request(self, params):
        self.last_error = None
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if data.get("Response") == "False":
                self.last_error = data.get("Error", "Movie not found.")
                print(self.last_error)
                return None
            return data

        except requests.exceptions.ConnectionError:
            self.last_error = "No internet connection."
            print(self.last_error)
        except requests.exceptions.Timeout:
            self.last_error = "The movie service took too long to respond."
            print(self.last_error)
        return None

    def search_by_title(self, title, year=None):
        params = {"apikey": self.api_key, "t": title}
        if year:
            params["y"] = year
        return self.send_api_request(params)

    def search_by_id(self, imdb_id):
        params = {"apikey": self.api_key, "i": imdb_id}
        return self.send_api_request(params)

    def search_by_keyword(self, keyword):
        params = {"apikey": self.api_key, "s": keyword}
        result = self.send_api_request(params)
        if result:
            return result.get("Search", [])
        else:
            return []

    # Displays information about a specific movie
    def display_movie(self, movie):
        print("\n" + "=" * 45)
        print(f"{movie.get('Title')} ({movie.get('Year')})")
        print("=" * 45)
        print(f"Genre:       {movie.get('Genre')}")
        print(f"Director:    {movie.get('Director')}")
        print(f"Actors:      {movie.get('Actors')}")
        print(f"IMDb rating: {movie.get('imdbRating')} / 10")
        print(f"Runtime:     {movie.get('Runtime')}")
        print(f"Plot:        {movie.get('Plot')}")
        print("=" * 45)

    # Displays a list of movies found by keyword
    def display_search_results(self, movies):
        if not movies:
            print("\nNo results found for this search.\n")
            return

        print(f"\nFound {len(movies)} results:")
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie['Title']} ({movie['Year']})")

    def add_to_favorites(self, movie):
        for favorite in self.favorites:
            if favorite["imdbID"] == movie["imdbID"]:
                print("This movie is already in your favorites.")
                return False

        self.favorites.append({
            "imdbID": movie.get("imdbID"),
            "title": movie.get("Title"),
            "year": movie.get("Year"),
            "rating": movie.get("imdbRating"),
            "genre": movie.get("Genre"),
            "poster": movie.get("Poster")
        })

        self.save_favorites()
        print(f"'{movie.get('Title')}' was added to your favorites.")
        return True

    def display_favorites(self):
        if not self.favorites:
            print("\nYour favorites list is empty.\n")
            return

        for movie in self.favorites:
            if movie["rating"] in (None, "N/A"):
                movie["sort_rating"] = 0
            else:
                movie["sort_rating"] = float(movie["rating"])

        def sort_movies(movie):
            return movie["sort_rating"]

        self.favorites.sort(key=sort_movies, reverse=True)

        print("\n--- Favorite Movies ---")
        for i, movie in enumerate(self.favorites, 1):
            print(
                f"{i}. {movie['title']} ({movie['year']}) "
                f"— rating {movie['rating']} — {movie['genre']}"
            )

        for movie in self.favorites:
            del movie["sort_rating"]

    def remove_from_favorites(self, title):
        for movie in self.favorites:
            if movie["title"].lower() == title.lower():
                self.favorites.remove(movie)
                self.save_favorites()
                print(f"'{title}' was removed from your favorites.")
                return

        print("Movie with that title was not found.")

    def remove_by_id(self, imdb_id):
        for movie in self.favorites:
            if movie["imdbID"] == imdb_id:
                self.favorites.remove(movie)
                self.save_favorites()
                return movie
        return None


def main():
    print("Welcome to Movie Library!\n")

    try:
        app = MovieLibrary(API_KEY)
    except ValueError as e:
        print(e)
        return


    while True:
        print("""
1. Search for a movie by exact title
2. Search for movies by keyword
3. Show favorite movies
4. Remove a movie from favorites
5. Exit
""")
        choice = input("Your choice: ").strip()

        if choice == "1":
            title = input("Enter the exact movie title: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue

            movie = app.search_by_title(title)
            if movie:
                app.display_movie(movie)
                if input("Add to favorites? (y/n): ").strip().lower() == "y":
                    app.add_to_favorites(movie)

        elif choice == "2":
            keyword = input("Enter part of the title or a keyword: ").strip()
            if not keyword:
                print("Keyword cannot be empty.")
                continue

            app.display_search_results(app.search_by_keyword(keyword))

        elif choice == "3":
            app.display_favorites()

        elif choice == "4":
            title = input("Enter the exact movie title to remove: ").strip()
            app.remove_from_favorites(title)

        elif choice == "5":
            print("\nGoodbye!")
            break

        else:
            print("Invalid option, please try again.\n")


if __name__ == "__main__":
    main()
