import pandas as pd
from backend.modules.docvec_function import document_vector
from backend.modules.create_db import Text, db, tfidf_search_func, w2v_search_func
from sqlalchemy import text
from backend.models import SearchRequest, SearchType


def search(search_q: SearchRequest, model):
    """
    Выполняет поиск наиболее похожих текстов в базе данных на основе заданного запроса и метода поиска.

    Args:
        query (str): Входной текст запроса, который нужно искать.
        search_type (str): Тип поиска. Возможные значения:
            - 'w2v' для поиска на основе word2vec векторов.
            - 'tfidf' для поиска на основе TF-IDF.
        top_n (int): Количество наиболее похожих текстов, которые следует вернуть.
        model: Модель для векторизации текста

    Returns:
        pd.Series: Серия из топ-N текстов, наиболее похожих на запрос.

    Этапы:
    1. Предобрабатывает запрос с использованием функции `preprocess_pos_and_text`.
    2. В зависимости от выбранного типа поиска ('w2v' или 'tfidf') извлекает вектор запроса.
    3. Нормализует вектор запроса.
    4. Вычисляет косинусное сходство между вектором запроса и векторами в базе данных.
    5. Возвращает топ-N текстов с наибольшим сходством.
    """

    db.session.execute(text(w2v_search_func))
    db.session.execute(text(tfidf_search_func))
    query = search_q.query
    search_type = search_q.search_type
    top_n = search_q.quantity

    preprocessed_q = preprocess_pos_and_text(preprocess(query))

    if search_type == SearchType.w2v:
        preprocessed_q = preprocessed_q[0]
        q_vector = document_vector(preprocessed_q, model)
        q_norm = normalize(q_vector)
        call_func = f'''
            SELECT * FROM find_top_n_similar_vectors_w2v(
                '{list(q_vector)}', -- Новый вектор в формате JSON
                {q_norm},              -- Норма нового вектора 
                {top_n}               -- Вернуть n самых близких векторов
            );
            '''
        tops = db.session.execute(text(call_func)).fetchall()
        
    else:
        preprocessed_q = preprocessed_q[1]
        q_vector = model.transform([preprocessed_q]).toarray()[0]
        q_norm = normalize(q_vector)
        call_func = f'''
                    SELECT * FROM find_top_n_similar_vectors_tfidf(
                        '{list(q_vector)}', -- Новый вектор в формате JSON
                        {q_norm},              -- Норма нового вектора 
                        {top_n}               -- Вернуть n самых близких векторов
                    );
                    '''
        tops = db.session.execute(text(call_func)).fetchall()
    top_texts = []
    for i in range(len(tops)):
        top_text = Text.query.filter(Text.message_id == tops[i][0]).all()
        top_texts.append(top_text[0].text)

    return top_texts, tops

