from fastapi import FastAPI
from routers import out_api
from data.apikey import enableApiKey

summary="Microservicio que se encarga de todo lo relativo a mátricas"

app=FastAPI(
    title="events",
    version="0.0.1",
    summary=summary,
    docs_url='/api-docs'
)

enableApiKey()

app.include_router(out_api.router)