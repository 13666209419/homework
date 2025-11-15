"""
Utilities for scraping the Douban Top 250 movies list.

The scraper uses `requests` together with BeautifulSoup to fetch and parse
movie metadata from https://movie.douban.com/top250. Results are cached to
`data/douban_top250.json` to avoid repeatedly hammering the website.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import random
import time
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://movie.douban.com/top250"


@dataclass
class Movie:
    """Container for the metadata of a single movie."""

    rank: int
    title: str
    original_title: Optional[str]
    year: Optional[int]
    country: Optional[str]
    genres: List[str]
    rating: float
    votes: int
    quote: Optional[str]
    detail_url: str
    poster_url: Optional[str] = None
    is_playable: bool = False
    directors: List[str] = None
    actors: List[str] = None
    
    def __post_init__(self):
        """Initialize mutable default fields."""
        if self.directors is None:
            self.directors = []
        if self.actors is None:
            self.actors = []


class DoubanTop250Scraper:
    """Scrape the Douban Top 250 movie list."""

    def __init__(
        self,
        cache_dir: str | Path = "data",
        *,
        cache_filename: str = "douban_top250.json",
        use_cache: bool = True,
        min_delay: float = 1.0,
        max_delay: float = 2.5,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.cache_dir / cache_filename
        self.use_cache = use_cache
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/118.0.0.0 Safari/537.36"
                ),
                "Referer": BASE_URL,
            }
        )

    # Public API -----------------------------------------------------------------
    def fetch_movies(self, *, force_refresh: bool = False) -> List[Movie]:
        """Fetch and return a list of `Movie` instances."""
        if self.use_cache and not force_refresh and self.cache_path.exists():
            return self._load_from_cache()

        movies: List[Movie] = []
        for start in range(0, 250, 25):
            page_movies = self._fetch_page(start=start)
            movies.extend(page_movies)
            self._respectful_delay()

        if self.use_cache:
            self._write_cache(movies)

        return movies

    # Internal helpers -----------------------------------------------------------
    def _fetch_page(self, *, start: int) -> List[Movie]:
        """Fetch a single page of the toplist."""
        params = {"start": start}
        response = self.session.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        grid_view = soup.find("ol", class_="grid_view")
        if not grid_view:
            raise ValueError("Unable to locate movies list on the page.")

        movies: List[Movie] = []
        for li in grid_view.find_all("li"):
            try:
                movie = self._parse_movie(li)
                movies.append(movie)
            except Exception as exc:  # pragma: no cover - defensive parsing
                print(f"Skipping movie due to parsing error: {exc}")
        return movies

    def _parse_movie(self, li) -> Movie:
        """解析单个电影条目的HTML结构"""
        # 排名
        rank_tag = li.find("em")
        rank = int(rank_tag.get_text(strip=True)) if rank_tag else 0

        # 标题 - 可能有多个title span，第一个是中文名，第二个可能是英文名
        title_tags = li.find_all("span", class_="title")
        title = ""
        original_title = None
        
        if title_tags:
            title = title_tags[0].get_text(strip=True)
            # 如果有第二个title，通常是英文名
            if len(title_tags) > 1:
                second_title = title_tags[1].get_text(strip=True).lstrip("/").strip()
                if second_title:
                    original_title = second_title
        
        # 其他标题（别名）
        other_title_tag = li.find("span", class_="other")
        if other_title_tag and not original_title:
            other_text = other_title_tag.get_text(strip=True).lstrip("/").strip()
            if other_text:
                # 如果有多个别名，取第一个
                original_title = other_text.split("/")[0].strip() if "/" in other_text else other_text

        # 详情链接和海报
        detail_link = li.find("a")
        detail_url = detail_link["href"] if detail_link and detail_link.has_attr("href") else ""
        
        # 海报图片链接
        poster_url = None
        img_tag = li.find("img")
        if img_tag and img_tag.has_attr("src"):
            poster_url = img_tag["src"]

        # 是否可播放
        is_playable = False
        playable_tag = li.find("span", class_="playable")
        if playable_tag:
            is_playable = True

        # 导演和演员信息
        directors: List[str] = []
        actors: List[str] = []
        info_block = li.find("p")
        
        if info_block:
            info_text = info_block.get_text(strip=True)
            # 查找"导演"和"主演"的相关信息
            try:
                if "导演:" in info_text:
                    # 提取导演信息
                    director_part = info_text.split("主演:")[0] if "主演:" in info_text else info_text
                    if "导演:" in director_part:
                        director_parts = director_part.split("导演:")
                        if len(director_parts) > 1:
                            director_text = director_parts[1].strip()
                            # 解析导演名单（通常以 / 分隔）
                            director_list = [d.strip() for d in director_text.split("/") if d.strip()]
                            directors = director_list[:3]  # 取前三个导演
                
                if "主演:" in info_text:
                    # 提取演员信息
                    actors_parts = info_text.split("主演:")
                    if len(actors_parts) > 1:
                        actors_part = actors_parts[1]
                        # 查找是否有"<br"或其他分隔符
                        actors_text = actors_part.split("<br")[0] if "<br" in actors_part else actors_part
                        # 解析演员名单（通常以 / 分隔）
                        actor_list = [a.strip() for a in actors_text.split("/") if a.strip()]
                        actors = actor_list[:5]  # 取前五个演员
            except (IndexError, AttributeError, TypeError):
                # 忽略导演/演员提取错误
                pass

        # 年份、国家、类型信息
        year = country = None
        genres: List[str] = []
        
        if info_block:
            # 获取所有文本行
            info_text_full = info_block.get_text(separator="\n", strip=True)
            info_lines = [line.strip() for line in info_text_full.split("\n") if line.strip()]
            
            # 最后一行通常是：年份 / 国家 / 类型1 / 类型2 ...
            if info_lines:
                metadata_line = info_lines[-1]
                # 替换 &nbsp; 和其他空白字符
                metadata_line = metadata_line.replace("\xa0", " ").replace("&nbsp;", " ")
                # 按 / 分割
                parts = [part.strip() for part in metadata_line.split("/") if part.strip()]
                
                if parts:
                    # 第一部分是年份
                    year = _safe_int(parts[0])
                    # 第二部分是国家
                    if len(parts) > 1:
                        country = parts[1]
                    # 剩余部分是类型
                    if len(parts) > 2:
                        genres = parts[2:]

        # 评分
        rating_tag = li.find("span", class_="rating_num")
        rating = 0.0
        if rating_tag:
            rating_text = rating_tag.get_text(strip=True)
            try:
                rating = float(rating_text)
            except (ValueError, TypeError):
                rating = 0.0

        # 评价人数 - 在评分后面的span中
        votes = 0
        rating_div = li.find("div", class_="bd")
        if rating_div:
            # 查找包含"人评价"的span
            vote_spans = rating_div.find_all("span")
            for span in vote_spans:
                span_text = span.get_text(strip=True)
                if "人评价" in span_text or "评价" in span_text:
                    votes = _extract_vote_count(span_text)
                    break
        
        # 如果没找到，尝试从star div中查找
        if votes == 0:
            star_div = li.find("div", class_="star")
            if star_div:
                vote_spans = star_div.find_all("span")
                if vote_spans:
                    last_span = vote_spans[-1]
                    votes = _extract_vote_count(last_span.get_text(strip=True))

        # 经典台词/短评
        quote_tag = li.find("span", class_="inq")
        quote = quote_tag.get_text(strip=True) if quote_tag else None

        return Movie(
            rank=rank,
            title=title,
            original_title=original_title,
            year=year,
            country=country,
            genres=genres,
            rating=rating,
            votes=votes,
            quote=quote,
            detail_url=detail_url,
            poster_url=poster_url,
            is_playable=is_playable,
            directors=directors,
            actors=actors,
        )

    def _respectful_delay(self) -> None:
        """Sleep for a random interval to avoid hammering Douban."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def _write_cache(self, movies: Iterable[Movie]) -> None:
        data = [asdict(movie) for movie in movies]
        self.cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_from_cache(self) -> List[Movie]:
        raw = json.loads(self.cache_path.read_text(encoding="utf-8"))
        return [Movie(**movie_dict) for movie_dict in raw]


def _safe_int(value: str | None) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_vote_count(value: str) -> int:
    digits = "".join(char for char in value if char.isdigit())
    return int(digits) if digits else 0


__all__ = ["DoubanTop250Scraper", "Movie"]

