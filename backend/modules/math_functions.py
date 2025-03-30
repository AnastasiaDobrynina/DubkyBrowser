import numpy as np


def normalize(vec):
    return np.linalg.norm(vec)


def cosine_sim(vec1, vec2, norm1, norm2):
    float_vec2 = []
    for el in vec2[1:-1].split(', '):
        float_vec2.append(float(el))
    scalar_mul = np.dot(vec1, float_vec2)
    return scalar_mul / (norm1 * norm2)

