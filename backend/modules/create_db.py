from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class Text(db.Model):
    __tablename__ = "texts"

    message_id = db.Column('id', db.Integer, primary_key=True)
    text = db.Column('text', db.Text,  nullable=False)


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    user_login = db.Column('login', db.Text, primary_key=True)
    user_name = db.Column('username', db.Text,  nullable=False)
    user_password = db.Column('password', db.Text, nullable=False)
    user_sex = db.Column('sex', db.Text)
    user_age = db.Column('age', db.Integer)

    def get_id(self):
        return self.user_login  # Возвращаем user_login как уникальный идентификатор


class Saved(db.Model):
    __tablename__ = "saved"
    message_id = db.Column('text_id', db.Integer, primary_key=True)
    user_name = db.Column('user_login', db.Text, primary_key=True)
    saved_query = db.Column('qurey', db.Text,  nullable=False)


w2v_search_func = '''
CREATE OR REPLACE FUNCTION find_top_n_similar_vectors_w2v(
    new_index json,
    new_norm double precision,
    n integer
)
RETURNS TABLE(existing_id integer, similarity double precision) AS $$
DECLARE
    new_index_vector double precision[];
    magnitude_new double precision;
BEGIN
    -- Преобразуем JSON в массив чисел для нового вектора
     new_index_vector := ARRAY(
        SELECT json_array_elements_text(new_index)::double precision
    );
    
    -- модуль нового вектора
    magnitude_new := new_norm;

    -- Основной запрос: вычисление косинусной близости и выбор N ближайших
    RETURN QUERY
    SELECT 
        t.id AS existing_id, -- Замените t.id на поле с идентификатором в вашей таблице
        CASE 
            WHEN magnitude_new = 0 OR t.norm_w2v = 0 THEN 0
            ELSE (
                
                    -- Скалярное произведение нового вектора с каждым старым
                    (SELECT SUM(n1::double precision * n2::double precision)
                     FROM unnest(new_index_vector) WITH ORDINALITY AS nv1(n1), 
                          unnest(
                              ARRAY(SELECT json_array_elements_text(t.index_w2v)::double precision)) WITH ORDINALITY AS nv2(n2)
                     WHERE nv1.ordinality = nv2.ordinality
                    ) /
                    -- Нормализация: произведение модулей
                    (magnitude_new * t.norm_w2v)
               )
        END AS similarity
    FROM texts AS t
    ORDER BY similarity DESC -- Сортируем по убыванию косинусной близости
    LIMIT n; -- Ограничиваем выбор N ближайших векторов
END;
$$ LANGUAGE plpgsql;
'''

tfidf_search_func = '''
    CREATE OR REPLACE FUNCTION find_top_n_similar_vectors_tfidf(
    new_index json,
    new_norm double precision,
    n integer
)
RETURNS TABLE(existing_id integer, similarity double precision) AS $$
DECLARE
    new_index_vector double precision[];
    magnitude_new double precision;
BEGIN
    -- Преобразуем JSON в массив чисел для нового вектора
     new_index_vector := ARRAY(
        SELECT json_array_elements_text(new_index)::double precision
    );
    
    -- модуль нового вектора
    magnitude_new := new_norm;

    -- Основной запрос: вычисление косинусной близости и выбор N ближайших
    RETURN QUERY
    SELECT 
        t.id AS existing_id, -- Замените t.id на поле с идентификатором в вашей таблице
        CASE 
            WHEN magnitude_new = 0 OR t.norm_w2v = 0 THEN 0
            ELSE (
                
                    -- Скалярное произведение нового вектора с каждым старым
                    (SELECT SUM(n1::double precision * n2::double precision)
                     FROM unnest(new_index_vector) WITH ORDINALITY AS nv1(n1), 
                          unnest(
                              ARRAY(SELECT json_array_elements_text(t.index_tfidf)::double precision)) WITH ORDINALITY AS nv2(n2)
                     WHERE nv1.ordinality = nv2.ordinality
                    ) /
                    -- Нормализация: произведение модулей
                    (magnitude_new * t.norm_tfidf)
               )
        END AS similarity
    FROM texts AS t
    ORDER BY similarity DESC -- Сортируем по убыванию косинусной близости
    LIMIT n; -- Ограничиваем выбор N ближайших векторов
END;
$$ LANGUAGE plpgsql;
'''



