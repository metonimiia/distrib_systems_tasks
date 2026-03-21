import requests
from client import build_payload

URL = "http://localhost:8080/api/graphql"

def handle_response(resp):
    data = resp.json()

    if "errors" in data:
        print("Errors:")
        for e in data["errors"]:
            print(e)

    if "data" in data:
        print("Data:")
        print(data["data"])

# Mutation (создание item)
mutation = """
mutation CreateItem($name: String!, $sku: String!) {
  createItem(name: $name, sku: $sku) {
    id
    name
    sku
  }
}
"""

variables = {
    "name": "Test Item",
    "sku": "SKU-012"
}

payload = build_payload(mutation, variables)
resp = requests.post(URL, json=payload)
handle_response(resp)

# Query (получение items)
query = """
query {
  items {
    id
    name
    sku
  }
}
"""

payload = build_payload(query, {})
resp = requests.post(URL, json=payload)
handle_response(resp)