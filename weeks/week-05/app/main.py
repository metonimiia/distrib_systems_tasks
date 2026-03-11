import json
import re
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Week 05 GraphQL API")


class ReviewCreate(BaseModel):
    name: str
    rating: int


class Review(ReviewCreate):
    id: int


db: list[dict[str, Any]] = []
counter = 1


GRAPHIQL_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>GraphiQL</title>
    <style>
      body { margin: 0; font-family: sans-serif; }
      #graphiql { height: 100vh; }
    </style>
    <link
      rel="stylesheet"
      href="https://unpkg.com/graphiql/graphiql.min.css"
    />
  </head>
  <body>
    <div id="graphiql">Loading...</div>
    <script
      crossorigin
      src="https://unpkg.com/react/umd/react.production.min.js"
    ></script>
    <script
      crossorigin
      src="https://unpkg.com/react-dom/umd/react-dom.production.min.js"
    ></script>
    <script
      crossorigin
      src="https://unpkg.com/graphiql/graphiql.min.js"
    ></script>
    <script>
      const fetcher = async (graphQLParams) => {
        const response = await fetch("/graphql", {
          method: "post",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(graphQLParams),
        });
        return response.json();
      };

      ReactDOM.render(
        React.createElement(GraphiQL, { fetcher }),
        document.getElementById("graphiql"),
      );
    </script>
  </body>
</html>
"""


def _parse_arguments(raw_args: str, variables: dict[str, Any]) -> dict[str, Any]:
    args: dict[str, Any] = {}
    if not raw_args.strip():
        return args

    for key, value in re.findall(r"(\w+)\s*:\s*(\"[^\"]*\"|\$\w+|-?\d+)", raw_args):
        if value.startswith("$"):
            args[key] = variables.get(value[1:])
        elif value.startswith('"') and value.endswith('"'):
            args[key] = json.loads(value)
        else:
            args[key] = int(value)
    return args


def _select_fields(query: str, root_field: str) -> list[str]:
    pattern = rf"{root_field}(?:\s*\([^)]*\))?\s*\{{([^{{}}]+)\}}"
    match = re.search(pattern, query, re.DOTALL)
    if not match:
        return ["id", "name", "rating"]

    fields_block = match.group(1)
    return re.findall(r"\b[a-zA-Z_]\w*\b", fields_block)


def _project_review(item: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: item[field] for field in fields if field in item}


def _execute_graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    global counter

    variables = variables or {}
    compact_query = re.sub(r"\s+", " ", query).strip()

    if "createReview" in compact_query:
        match = re.search(r"createReview\s*\((.*?)\)", compact_query)
        if not match:
            return {"errors": [{"message": "Invalid createReview mutation"}]}

        args = _parse_arguments(match.group(1), variables)
        if not isinstance(args.get("name"), str) or not isinstance(args.get("rating"), int):
            return {"errors": [{"message": "createReview requires name and rating"}]}

        item = {"id": counter, "name": args["name"], "rating": args["rating"]}
        db.append(item)
        counter += 1

        fields = _select_fields(compact_query, "createReview")
        return {"data": {"createReview": _project_review(item, fields)}}

    if re.search(r"\breview\s*\(", compact_query):
        match = re.search(r"review\s*\((.*?)\)", compact_query)
        if not match:
            return {"errors": [{"message": "Invalid review query"}]}

        args = _parse_arguments(match.group(1), variables)
        review_id = args.get("id")
        if not isinstance(review_id, int):
            return {"errors": [{"message": "review query requires id"}]}

        item = next((entry for entry in db if entry["id"] == review_id), None)
        fields = _select_fields(compact_query, "review")
        return {
            "data": {
                "review": None if item is None else _project_review(item, fields),
            }
        }

    if re.search(r"\breviews\b", compact_query):
        fields = _select_fields(compact_query, "reviews")
        return {"data": {"reviews": [_project_review(item, fields) for item in db]}}

    return {"errors": [{"message": "Unsupported operation"}]}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Open /graphql for GraphQL queries."}


@app.get("/graphql", response_class=HTMLResponse)
async def graphql_playground() -> str:
    return GRAPHIQL_HTML


@app.post("/graphql")
async def graphql_endpoint(request: Request) -> JSONResponse:
    payload = await request.json()
    query = payload.get("query")
    variables = payload.get("variables")

    if not isinstance(query, str) or not query.strip():
        return JSONResponse(
            status_code=400,
            content={"errors": [{"message": "Request body must contain a query string"}]},
        )

    result = _execute_graphql(query, variables)
    status_code = 200 if "data" in result else 400
    return JSONResponse(status_code=status_code, content=result)
