from fastapi import FastAPI
from .dispatch_endpoint import router as dispatch_router
from .merge_endpoint import router as merge_router

app = FastAPI(title="GenesisCore API", version="2.0")

app.include_router(dispatch_router, prefix="/dispatch")
app.include_router(merge_router, prefix="/merge")
