# coding: utf-8

import abc
import logging
import typing as t
from dataclasses import dataclass
from uuid import UUID

from interfaces import Resource, Resources
from opensearchpy import NotFoundError, OpenSearch

resources = Resources()


class SearchService(abc.ABC):
    def search(
        self,
        kinds: t.List[Resource],
        tenants_id: UUID,
        companies_id: UUID,
        query: t.Dict[str, t.Any],
    ) -> t.Dict[t.Literal["hits"], t.Dict[str, t.Any]]:
        raise NotImplementedError

    def delete_index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
        data: t.Dict[str, t.Any],
    ) -> None:
        raise NotImplementedError

    def index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
        data: t.Dict[str, t.Any],
    ) -> t.Dict[str, t.Any]:
        raise NotImplementedError

    def delete_document(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
        document_id: str,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        raise NotImplementedError

    def create_index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
        data: t.Dict[str, t.Any],
    ) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class HTTPOpenSearchService(SearchService):
    client: OpenSearch

    def _gen_index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
    ) -> str:
        return (
            f"tenant_{str(UUID(str(tenants_id)))}"
            f"_company_{str(UUID(str(companies_id)))}"
            f"_kind_{kind.name}"
        )

    def index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
        data: t.Dict[str, t.Any],
    ) -> t.Dict[str, t.Any]:
        self.client.index(
            index=self._gen_index(kind, tenants_id, companies_id),
            body=data,
            id=data.get("id"),
        )
        return data

    def delete_index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
    ) -> None:
        try:
            index = self._gen_index(kind, tenants_id, companies_id)
            if self.client.indices.exists(index):
                self.client.indices.delete(index)
        except NotFoundError:
            pass

    def create_index(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
    ) -> None:
        body: t.Dict[str, t.Any] = {}
        self.client.indices.create(
            index=self._gen_index(kind, tenants_id, companies_id),
            body=body,
        )

    def search(
        self,
        kinds: t.List[Resource],
        tenants_id: UUID,
        companies_id: UUID,
        query: t.Dict[str, t.Any],
    ) -> t.Dict[t.Literal["hits"], t.Dict[str, t.Any]]:
        return self.client.search(
            index=",".join(
                [self._gen_index(kind, tenants_id, companies_id) for kind in kinds]
            ),
            body={"query": query},
        )

    def delete_document(
        self,
        kind: Resource,
        tenants_id: UUID,
        companies_id: UUID,
        document_id: str,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        try:
            response = self.client.delete(
                index=self._gen_index(kind, tenants_id, companies_id),
                id=document_id,
            )
            return response
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            return None
