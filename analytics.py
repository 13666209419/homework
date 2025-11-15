"""
Analytical helpers for the Douban Top 250 dataset.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np
import pandas as pd

from scraper import Movie


def movies_to_dataframe(movies: Iterable[Movie]) -> pd.DataFrame:
    """Convert an iterable of `Movie` dataclasses to a tidy DataFrame."""
    records = [
        {
            "rank": movie.rank,
            "title": movie.title,
            "original_title": movie.original_title,
            "year": movie.year,
            "country": movie.country,
            "genres": movie.genres,
            "rating": movie.rating,
            "votes": movie.votes,
            "quote": movie.quote,
            "detail_url": movie.detail_url,
        }
        for movie in movies
    ]
    df = pd.DataFrame(records)
    if not df.empty:
        df["decade"] = df["year"].apply(_year_to_decade)
        df["primary_genre"] = df["genres"].apply(lambda items: items[0] if items else None)
        df["all_genres"] = df["genres"].apply(lambda items: ", ".join(items))
    return df


def load_cached_movies(cache_path: str | Path) -> pd.DataFrame:
    """Load cached movies from a JSON file into a DataFrame."""
    cache_file = Path(cache_path)
    if not cache_file.exists():
        raise FileNotFoundError(
            f"Cache file {cache_file} not found. Run the scraper to populate it."
        )
    data = pd.read_json(cache_file)
    if "genres" in data.columns:
        data["genres"] = data["genres"].apply(lambda x: x if isinstance(x, list) else [])
        data["all_genres"] = data["genres"].apply(lambda xs: ", ".join(xs))
        data["primary_genre"] = data["genres"].apply(lambda xs: xs[0] if xs else None)
    if "year" in data.columns:
        data["decade"] = data["year"].apply(_year_to_decade)
    return data


def rating_summary(df: pd.DataFrame) -> pd.Series:
    """Return simple descriptive statistics of ratings."""
    return df["rating"].describe()


def votes_summary(df: pd.DataFrame) -> pd.Series:
    """Return descriptive statistics for vote counts."""
    return df["votes"].describe()


def movies_per_country(df: pd.DataFrame, *, top_n: Optional[int] = None) -> pd.Series:
    """Aggregate movies by country."""
    counts = (
        df.assign(country=df["country"].fillna("未知国家"))
        .groupby("country")["title"]
        .count()
        .sort_values(ascending=False)
    )
    if top_n:
        counts = counts.head(top_n)
    return counts


def movies_per_decade(df: pd.DataFrame) -> pd.Series:
    """Aggregate movies by decade."""
    return (
        df.dropna(subset=["decade"])
        .groupby("decade")["title"]
        .count()
        .sort_values(ascending=True)
    )


def rating_distribution(df: pd.DataFrame, bins: Optional[int] = None) -> pd.Series:
    """Return the rating distribution as a histogram counts series."""
    if bins is None:
        bins = max(5, int(df["rating"].nunique()))
    counts, bin_edges = np.histogram(df["rating"], bins=bins, range=(df["rating"].min(), 10))
    labels = [
        f"{bin_edges[i]:.1f} - {bin_edges[i + 1]:.1f}"
        for i in range(len(bin_edges) - 1)
    ]
    return pd.Series(counts, index=labels)


def genre_popularity(df: pd.DataFrame, *, top_n: Optional[int] = None) -> pd.Series:
    """Return counts of movies per genre."""
    exploded = df.explode("genres")
    counts = (
        exploded.dropna(subset=["genres"])
        .groupby("genres")["title"]
        .count()
        .sort_values(ascending=False)
    )
    if top_n:
        counts = counts.head(top_n)
    return counts


def _year_to_decade(year: Optional[int]) -> Optional[str]:
    if year is None or pd.isna(year):
        return None
    decade_start = int(year // 10 * 10)
    return f"{decade_start}s"


__all__ = [
    "movies_to_dataframe",
    "load_cached_movies",
    "rating_summary",
    "votes_summary",
    "movies_per_country",
    "movies_per_decade",
    "rating_distribution",
    "genre_popularity",
]

