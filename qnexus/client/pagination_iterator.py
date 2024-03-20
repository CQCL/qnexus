""" A class for iterating over paginated API endpoints, collecting any
IteratedType into a python Iterator."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generic, Iterator, List, TypeVar

import httpx
import pandas as pd


from qnexus.client import nexus_client
from qnexus.exceptions import ResourceFetchFailed
from qnexus.references import RefList


IteratedType = TypeVar("IteratedType")


class NexusDatabaseIterator(Generic[IteratedType], Iterator[IteratedType]):
    """An object that can be used to summarize or iterate through a filter query made to 
    the Nexus database. """

    def __init__(
        self,
        resource_type: str,
        nexus_url: str,
        params: Dict[str, Any],
        wrapper_method: Callable[[dict[str,Any]], List[IteratedType]],
    ) -> None:
        self.resource_type = resource_type
        self.nexus_url = nexus_url
        self.wrapper = wrapper_method
        self.current_page: int = 0
        self.params = params
        # TODO Could put these defaults somewhere better
        self.params["page[size]"] = self.params.get("page[size]", 50)
        self.params["filter[archived]"] = self.params.get("filter[archived]", False)
        self.params["filter[timestamps][created][after]"] = self.params.get(
            "filter[timestamps][created][after]", 
            datetime(day=1, month=1, year=2023, tzinfo=timezone.utc),
        ) # TODO Hack to avoid older broken circuits and projects (will affect old users)
        self._all = None
        

    def __iter__(self) -> Iterator[IteratedType]:
        return self
    
    def __next__(self) -> Any:

        self.params["page[number]"] = self.current_page,

        res = nexus_client.get(
            url=self.nexus_url,
            params=self.params
        )

        self.handle_errors(res)

        next_page = res.json()["data"]

        self.current_page += 1
        if next_page:
            return RefList(self.wrapper(res.json()))
        raise StopIteration
    
    def all(self, refresh: bool = False) -> RefList[IteratedType]:
        """Collapse into RefList. Pass refresh to refresh the data."""
        if refresh:
            self.__init__(
                resource_type=self.resource_type,
                nexus_url=self.nexus_url,
                params=self.params,
                wrapper_method=self.wrapper
            )
        if not self._all:
            self._all = RefList([])
            for x in self:
                self._all.extend(x)
        return self._all
    
    def count(self) -> int:
        """Count the items that match the filter."""
        summary_params = self.params.copy()
        summary_params["page[size]"] = 1

        res = nexus_client.get(
            url=self.nexus_url,
            params=self.params
        )

        self.handle_errors(res)
        
        res_dict = res.json()
        return res_dict["meta"]["total_count"]
    

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""

        summary_params = self.params.copy()
        summary_params["page[size]"] = 1

        res = nexus_client.get(
            url=self.nexus_url,
            params=self.params
        )

        self.handle_errors(res)
        
        res_dict = res.json()
        meta = res_dict["meta"]

        return pd.DataFrame({
            "resource": self.resource_type,
            "total_count": meta["total_count"]
        }, index=[0])
    
    def handle_errors(self, res: httpx.Response) -> None:
        """ """
        if res.status_code != 200:
            raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)
