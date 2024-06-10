""" A class for iterating over paginated API endpoints, collecting any
iterated type T into a python Iterator."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generic, Iterator, List, TypeVar

import httpx
import pandas as pd

import qnexus.exceptions as qnx_exc
from qnexus.references import Dataframable, DataframableList

T = TypeVar("T", bound=Dataframable)


class DatabaseIterator(Generic[T], Iterator[T]):
    """An object that can be used to summarize or iterate through a filter query made to
    the Nexus database."""

    def __init__(
        self,
        resource_type: str,
        nexus_url: str,
        params: Dict[str, Any],
        wrapper_method: Callable[[dict[str, Any]], List[T]],
        nexus_client: httpx.Client,
    ) -> None:
        self.nexus_client = nexus_client
        self.resource_type = resource_type
        self.nexus_url = nexus_url
        self.wrapper = wrapper_method
        self.current_page: int = 0
        self.params = params
        self._cached_list: DataframableList[T] | None = None
        self._current_page_subiterator: Iterator[T] = iter([])
        # TODO Hack to avoid older broken circuits and projects (will affect old users)
        self.params["filter[timestamps][created][after]"] = self.params.get(
            "filter[timestamps][created][after]",
            datetime(day=1, month=1, year=2023, tzinfo=timezone.utc),
        )

    def __iter__(self) -> Iterator[T]:
        """Return the Iterator."""
        return self

    def __next__(self) -> T:
        """Get the next element of the Iterator."""
        # TODO check performance
        try:
            return next(self._current_page_subiterator)
        except StopIteration as exc:
            self.params["page[number]"] = (self.current_page,)
            res = self.nexus_client.get(url=self.nexus_url, params=self.params)

            self._handle_errors(res)
            self.current_page += 1

            if res.json()["data"]:
                self._current_page_subiterator = iter(self.wrapper(res.json()))
                return next(self._current_page_subiterator)
            raise StopIteration from exc

    def list(self) -> DataframableList[T]:
        """Collapse into RefList."""
        if not self._cached_list:
            self._cached_list = DataframableList([])
            for item in self:
                self._cached_list.append(item)
        return self._cached_list

    def df(self) -> pd.DataFrame:
        """List and present in a pandas DataFrame."""
        return self.list().df()

    def count(self) -> int:
        """Count the items that match the filter."""
        summary_params = self.params.copy()
        summary_params["page[size]"] = 1

        res = self.nexus_client.get(url=self.nexus_url, params=self.params)

        self._handle_errors(res)

        res_dict = res.json()
        return res_dict["meta"]["total_count"]

    def summarize(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {"resource": self.resource_type, "total_count": self.count()}, index=[0]
        )

    def _handle_errors(self, res: httpx.Response) -> None:
        """Consolidated error handling."""
        if res.status_code != 200:
            raise qnx_exc.ResourceFetchFailed(
                message=res.json(), status_code=res.status_code
            )

    def try_unique_match(self) -> T:
        """Utility function for expecting a single match on the filter."""
        match_count = self.count()

        if match_count > 1:
            raise qnx_exc.NoUniqueMatch()
        if match_count == 0:
            raise qnx_exc.ZeroMatches()
        return self.list()[0]
