from typing import Annotated
from fastapi.responses import JSONResponse

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import json
from SCRAPING.index import scrape
from threading import Thread
import pymongo

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password 2")
    user = UserInDB(**user_dict)
    print(user)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password 1")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/data")
async def read_data(current_user: Annotated[User, Depends(get_current_active_user)]):
    with open("dataset.json", "r") as f:
        data = json.load(f)
    print(remove_array_keys(data))
    return JSONResponse(content=remove_array_keys(data))

@app.get('/scrape')
def start_scraping():
    t = Thread(target=scrape)
    t.daemon = True
    t.start()
    return 'Web scraping iniciado en segundo plano!'


@app.get('/registers')
def get_registers(current_user: Annotated[User, Depends(get_current_active_user)]):
    client = pymongo.MongoClient("mongodb://mongodb:mongodb@localhost:27017/")
    db = client["api"]
    col = db["dataset"]
    return list(col.find({}, {"_id": 0, "id": 1, "type": 1}))


@app.get('/registers/{id}/{type}')
def get_process(id: str, type: str):
    client = pymongo.MongoClient("mongodb://mongodb:mongodb@localhost:27017/")
    db = client["api"]
    col = db["dataset"]

    print({"id": id, "type": type})
    procces = col.find({"id": id, "type": type}, {"_id": 0 ,"process.deatails": 0,"process.details": 0 })

    return list(procces)


@app.get('/registers/{id}/{type}/process/{no}')
def get_process_details(id: str, type: str, no: str):
    client = pymongo.MongoClient("mongodb://mongodb:mongodb@localhost:27017/")
    db = client["api"]
    col = db["dataset"]

    print({"id": id, "type": type,"process.no":no })
    procces = col.find({"id": id, "type": type, "process": {"$elemMatch": {"no": {"$ne": "1"}}}}, {"_id": 0 ,"process.deatails" : 0,"process.details": 0 })



    return list(procces)


def remove_array_keys(data):
    # Si el valor no es un diccionario, devuelve el valor tal cual
    if not isinstance(data, dict):
        return data

    # Crea un nuevo diccionario para almacenar los datos sin las claves que son arrays
    result = {}
    for key, value in data.items():
        # Si el valor es un array, omitir la clave
        if isinstance(value, list):
            continue
        # Si el valor es un diccionario, aplicar la función recursivamente
        elif isinstance(value, dict):
            result[key] = remove_array_keys(value)
        # De lo contrario, agregar el valor al diccionario de resultados
        else:
            result[key] = value

    return result



