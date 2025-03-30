from typing import List, Union
import numpy as np


def document_vector(doc: List[str], model) -> Union[np.ndarray, np.array]:
    """
    Преобразует документ в вектор с помощью усреднения векторов слов из модели Word2Vec.

    Args:
        doc (List[str]): Список токенов (слов) документа.
        model (Word2Vec): Предварительно обученная модель Word2Vec, из которой извлекаются векторы слов.

    Returns:
        Union[np.ndarray, np.array]: Усреднённый вектор документа. Если все слова отсутствуют в модели, возвращается нулевой вектор.
    """
    word_vectors = [model[word] for word in doc if word in model]
    
    return np.mean(word_vectors, axis=0) if word_vectors else np.zeros(model.vector_size)

