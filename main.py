from fastapi import FastAPI
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client

app = FastAPI()

# apm = make_apm_client(
#         {
#             'SERVICE_NAME': "fastapitest",
#             'SECRET_TOKEN': '',
#             'SERVER_URL': 'http://elastic:changeme@localhost:8200',
#             'ENVIRONMENT': 'production',
#         }
#     )
# app.add_middleware(ElasticAPM, client=apm)


@app.get("/")
async def root():
    return {"message": "Hello World"}