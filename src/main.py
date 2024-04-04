import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.base import router


app = FastAPI(
    title='FilesManager',
    docs_url='/docs',
    default_response_class=ORJSONResponse
)

app.include_router(
    router=router
)


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host='0.0.0.0'
    )
