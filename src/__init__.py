"""豆瓣电影 Top 250 爬虫和分析工具包"""

from .scraper import DoubanTop250Scraper, Movie
from .analytics import (
    movies_to_dataframe,
    load_cached_movies,
    rating_summary,
    votes_summary,
    movies_per_country,
    movies_per_decade,
    rating_distribution,
    genre_popularity,
)

__version__ = "1.0.0"

__all__ = [
    "DoubanTop250Scraper",
    "Movie",
    "movies_to_dataframe",
    "load_cached_movies",
    "rating_summary",
    "votes_summary",
    "movies_per_country",
    "movies_per_decade",
    "rating_distribution",
    "genre_popularity",
]

