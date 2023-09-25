from fastapi import FastAPI


app = FastAPI(
    title='IBAN Validator',
    debug=True
)


@app.get("/")
async def health():
    return {'health': 'ok'}
