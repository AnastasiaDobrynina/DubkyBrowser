from typing import List, Union, Tuple
from nltk.corpus import stopwords
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)

sw = stopwords.words('russian')

def preprocess(text: str) -> List[Tuple[str, str]]:
    """
    Предобрабатывает входной текст, выполняя токенизацию, приведение к нижнему регистру
    и фильтрацию стоп-слов и неалфавитных и нечисловых токенов.
   
    Args:
        text (str):  Входной текст для предобработки.
    
    Returns:
        List[Tuple[str, str]]:  Лист, содержащий леммы и части их речи. (lemmas).
    """
    lemmas = []
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
        token_str = str(token.lemma).lower()
        if token_str.isalpha() or token_str.isnumeric():  # числовые токены включаются
            if token_str not in sw:
                lemmas.append((token_str, token.pos))
    return lemmas


def preprocess_pos_and_text(preprocessed_lemmas: List[Tuple[str, str]]) -> Union[Tuple[List[List[str]], List[str]], None]:
    """
    Преобразует лемматизированные и размеченные по чати речи тексты в кортеж из двух спиков, содержащих данные для удобной векторизации
   
    Args:
       preprocessed_lemmas (List[Tuple[str, str]]):  Предобработанные тексты в виде лемм с частями речи.
    
    Returns:
        List[List[str]]:  Кортеж листов, удобных для работы с Word2vec и TF-IDF.
    """

    lemmas_list_pos = [str(lemma[0]) + '_' + str(lemma[1]) for lemma in preprocessed_lemmas]
    lemmas_text = ' '.join([str(lemma[0]) for lemma in preprocessed_lemmas])
            
    return (lemmas_list_pos, lemmas_text)

