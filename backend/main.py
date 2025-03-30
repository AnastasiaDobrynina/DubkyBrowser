from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from gensim.models import KeyedVectors
import pickle
import uvicorn
from fastapi.responses import JSONResponse
from sqlalchemy import func
from pydantic import ValidationError
from modules.preprocess_functions import preprocess
from modules.create_db import Users, Text, Saved
from models import *
from modules.search_function import search
from fastapi.middleware.cors import CORSMiddleware


model = KeyedVectors.load("./modules/w2v_model.bin")

with open("modules/tfidf_vectorizer.pkl", 'rb') as file:
    vectorizer = pickle.load(file)

app = FastAPI()
config = Settings()
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000", "http://localhost:5000"],  # Разрешить запросы с этих адресов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

DATABASE_URL = 'postgresql+psycopg2://postgres:password@localhost/db_dubky'
engine = create_engine(DATABASE_URL)

# Сессия для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/search_types", response_model=List[SearchType])
def get_search_types():
    """
    Возвращает доступные методы поиска: w2v и tf-idf.
    """
    return [
        SearchType.w2v,
        SearchType.tfidf
    ]


@app.get("/corpora_info", response_model=CorporaInfo)
def get_corpora_info(db: Session = Depends(get_db)):
    """
    Берет из базы информацию о корпусе: количество текстов и количество токенов.
    """
    num_texts = db.query(func.count(Text.message_id)).scalar()
    texts = db.query(Text.text).all()
    token_texts = []
    for text in texts:
        token_texts.append(preprocess(text.text))
    return CorporaInfo(num_texts=num_texts, num_tokens=len(token_texts))


@app.post("/search", response_model=SearchResult)
async def search_endpoint(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Делаем поиск с параметрами: text-q (текст запроса), quantity (количество результатов), type (тип поиска).
    """
    start_time = datetime.datetime.now()

    try:
        # Выбираем модель для поиска в зависимости от типа поиска
        if search_request.search_type == SearchType.w2v:
            model_to_use = model
        else:
            model_to_use = vectorizer

        # Получаем результаты поиска
        res_texts, res_tops = search(search_request, model_to_use, db)

        # Формируем список результатов
        res = [
            {"rank": i + 1, "text": text, "relevance": round(s, 3), "index": idx}
            for i, (text, (idx, s)) in enumerate(zip(res_texts, res_tops))
        ]

        current_time = datetime.datetime.now()
        uptime = current_time - start_time
        # Возвращаем результат в формате JSON
        return SearchResult(text_info=res,
                            quantity=search_request.quantity,
                            query=search_request.query,
                            search_type=search_request.search_type,
                            time=str(uptime)
                            )

    except ValidationError as errors:
        # Если возникает ошибка валидации, возвращаем ошибку
        raise HTTPException(status_code=400, detail=str(errors))


@app.post("/register", response_model=UserBase)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.user_login == user.login).first()
    print(existing_user)
    if existing_user:
        print('пользователь есть')
        return JSONResponse(
            status_code=400,
            content={"detail": "Пользователь с таким логином уже зарегестрирован"}
        )

    new_user = Users(
        user_login=user.login,
        user_name=user.name,
        user_password=user.password,
        user_sex=user.gender,
        user_age=user.age,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserBase(
        login=new_user.user_login,
        name=new_user.user_name,
        gender=new_user.user_sex,
        age=new_user.user_age,
    )


@app.post("/login", response_model=UserBase)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.user_login == credentials.login).first()
    if not user or user.user_password != credentials.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return UserBase(
        login=user.user_login,
        name=user.user_name,
        gender=user.user_sex,
        age=user.user_age,
    )


@app.get("/profile/{user_login}", response_model=UserBase)
def get_profile(user_login: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.user_login == user_login).first()
    saved_from_db = user.saved_items

    # saved = db.session.query(Saved).filter(Saved.user_name == current_user.user_login).all()
    # print(saved)
    saved_messages_ids = [m.message_id for m in saved_from_db]
    saved_messages = db.query(Text).filter(Text.message_id.in_(saved_messages_ids)).all()

    # print(saved_messages)
    # saved_messages_text = [[i + 1, m.text, s.saved_query, m.message_id] for i, (m, s) in
    #                        enumerate(zip(saved_messages, saved))]
    # print(saved_messages_text)
    saved_texts = []
    for i in range(len(saved_from_db)):
        one_message_info = {}
        one_message_info['rank'] = i+1
        one_message_info['id'] = saved_from_db[i].message_id
        one_message_info['text'] = saved_messages[i].text
        one_message_info['query'] = saved_from_db[i].saved_query
        saved_texts.append(one_message_info)

    saved = SavedMessages(text_info=saved_texts)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserBase(
        login=user.user_login,
        name=user.user_name,
        gender=user.user_sex,
        age=user.user_age,
        saved=saved
    )


@app.post("/save", response_model=SavedMessages)
def save(data: SaveRequest, db: Session = Depends(get_db)):
    if not data.user_name:
        raise HTTPException(status_code=400, detail="Необходимо войти или зарегестрироваться")

    # Добавляем в базу данных
    saved_item = Saved(message_id=data.message_id,
                        user_name=data.user_name,
                        saved_query=data.saved_query)
    try:
        db.add(saved_item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных")

    return JSONResponse(
        status_code=200,
        content={"detail": "Сообщение успешно лайкнуто"}
    )



@app.post("/unsave")
def unsave(data: SaveRequest, db: Session = Depends(get_db)):
    print(data)
    if not data.user_name:
        raise HTTPException(status_code=400, detail="Необходимо войти или зарегестрироваться")
    saved_item = db.query(Saved).filter_by(message_id=data.message_id, user_name=data.user_name).first()

    if saved_item:
        try:
            # Удалить запись из базы данных
            db.delete(saved_item)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при удалении данных")

    return JSONResponse(
        status_code=200,
        content={"detail": "Сообщение успешно дизлайкнуто"}
    )


if __name__ == "__main__":
    uvicorn.run(app, port=config.PORT, host=config.HOST)


