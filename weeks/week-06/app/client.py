PROJECT_CODE = "items-s12"


def build_payload(query: str, variables: dict) -> dict:
    return {
        "query": query,
        "variables": variables or {}
    }