# coding=utf-8

import logging
import os
import typing as t
from uuid import uuid4

import searchservice
from interfaces import Resources
from opensearchpy import OpenSearch

resources = Resources()

logging.basicConfig(level=logging.INFO)

search_service = searchservice.HTTPOpenSearchService(
    client=OpenSearch(
        hosts=[
            {
                "host": os.getenv("OPENSEARCH_HOST", "localhost"),
                "port": os.getenv("OPENSEARCH_PORT", "9200"),
            }
        ],
        http_auth=(
            os.getenv("OPENSEARCH_USERNAME", ""),
            os.getenv("OPENSEARCH_PASSWORD", ""),
        ),
        use_ssl=False,
        verify_certs=False,
    ),
)

tenants_id: str = "f0835e2d-bd68-406c-99a7-ad63a51e9ef9"
companies_id: str = "bf58c749-c90a-41e2-b66f-6d98aae17a6c"
search_str: str = "frank"
document_id_to_delete: str = str(uuid4())

fake_data: t.List[t.Dict[str, t.Any]] = [
    {"id": document_id_to_delete, "name": "Franklin", "tech": "python,node,golang"},
    {"id": str(uuid4()), "name": "Jarvis", "tech": "AI"},
    {"id": str(uuid4()), "name": "Parry", "tech": "Golang"},
    {"id": str(uuid4()), "name": "Steve", "tech": "iOS"},
    {"id": str(uuid4()), "name": "Frank", "tech": "node"},
]

search_service.delete_index(
    kind=resources.users, tenants_id=tenants_id, companies_id=companies_id
)

search_service.create_index(
    kind=resources.users,
    tenants_id=tenants_id,
    companies_id=companies_id,
)

for item in fake_data:
    search_service.index(
        kind=resources.users,
        tenants_id=tenants_id,
        companies_id=companies_id,
        data=dict(tenants_id=tenants_id, companies_id=companies_id, **item),
    )

search_query: t.Dict[str, t.Any] = {
    "bool": {
        "must": [],
        "must_not": [],
        "should": [],
        "filter": [
            {"term": {"tenants_id.keyword": tenants_id}},
            {"term": {"companies_id.keyword": companies_id}},
        ],
    }
}
search_query["bool"]["must"].append(
    {
        "multi_match": {
            "query": search_str,
            "type": "phrase_prefix",
            "fields": ["name", "tech"],
        }
    }
)

search_results = search_service.search(
    kinds=[resources.users],
    tenants_id=tenants_id,
    companies_id=companies_id,
    query=search_query,
)

final_result = search_results.get("hits", {}).get("hits", [])
for item in final_result:
    logging.info(["Item -> ", item.get("_source", {})])

deleted_result = search_service.delete_document(
    kind=resources.users,
    tenants_id=tenants_id,
    companies_id=companies_id,
    document_id=document_id_to_delete,
)
logging.info(["Deleted result -> ", deleted_result])

