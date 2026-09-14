import time
import threading

import requests

from app.config.settings import settings


class SemanticScholarService:

    BASE_URL = (
        "https://api.semanticscholar.org/"
        "recommendations/v1"
    )

    _lock = threading.Lock()
    _last_request_time = 0.0
    _REQUEST_INTERVAL = 1.0

    def _wait_for_rate_limit(self):
        with self._lock:
            now = time.monotonic()

            elapsed = now - self._last_request_time

            if elapsed < self._REQUEST_INTERVAL:
                time.sleep(
                    self._REQUEST_INTERVAL - elapsed
                )

            self._last_request_time = time.monotonic()

    def _get(
        self,
        url: str,
        params: dict,
        headers: dict,
    ):
        self._wait_for_rate_limit()

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15,
        )

        if response.status_code != 429:
            response.raise_for_status()
            return response

        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after:
            wait_time = float(retry_after)
        else:
            wait_time = 1.0

        time.sleep(wait_time)

        self._wait_for_rate_limit()

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        return response

    def get_paper_by_id(
        self,
        paper_id: str,
    ) -> dict:

        url = (
            "https://api.semanticscholar.org/"
            "graph/v1/paper/"
            f"{paper_id}"
        )

        params = {
            "fields": "paperId,title,doi",
        }

        headers = {}

        if settings.SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = (
                settings.SEMANTIC_SCHOLAR_API_KEY
            )

        response = self._get(
            url=url,
            params=params,
            headers=headers,
        )

        return response.json()

    def recommend_papers(
        self,
        paper_id: str,
        limit: int = 5,
    ) -> list[dict]:

        url = (
            f"{self.BASE_URL}/papers/"
            f"forpaper/{paper_id}"
        )

        params = {
            "fields": (
                "title,authors,year,url,"
                "abstract,citationCount"
            ),
            "limit": limit,
        }

        headers = {}

        if settings.SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = (
                settings.SEMANTIC_SCHOLAR_API_KEY
            )

        response = self._get(
            url=url,
            params=params,
            headers=headers,
        )

        data = response.json()

        return data.get(
            "recommendedPapers",
            []
        )

    def search_paper(
        self,
        title: str,
        limit: int = 1,
    ) -> dict | None:

        url = (
            "https://api.semanticscholar.org/"
            "graph/v1/paper/search"
        )

        params = {
            "query": title,
            "limit": limit,
            "fields": (
                "paperId,title,authors,"
                "year,doi"
            ),
        }

        headers = {}

        if settings.SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = (
                settings.SEMANTIC_SCHOLAR_API_KEY
            )

        response = self._get(
            url=url,
            params=params,
            headers=headers,
        )

        data = response.json()

        papers = data.get(
            "data",
            []
        )

        if not papers:
            return None

        return papers[0]