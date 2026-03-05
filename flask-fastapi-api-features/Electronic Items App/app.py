from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from helper import ItemResponse ,ItemNotFoundException , get_items



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": f"Item with id {exc.item_id} not found"}
    )


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):

    items = get_items()

    for item in items:
        if item["id"] == item_id:
            return {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "message": "Item details fetched successfully"
            }

    raise ItemNotFoundException(item_id)


@app.get("/v1/items")
def get_items_v1():
    items = get_items()
    return [{"id": item["id"], "name": item["name"]} for item in items]


@app.get("/v2/items")
def get_items_v2():
    return get_items()