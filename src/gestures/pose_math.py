import numpy as np
from collections import deque

def lm_xy(landmarks, idx):
    lm = landmarks[idx]
    return np.array([lm.x, lm.y], dtype = np.float32), lm.visibility

def distance(a, b):
    return float(np.linalg.norm(a - b))

def angle(a, b, c):
    ba = a - b
    bc = c - b
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-9)
    cosang = np.clip(cosang, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def avg(a, b):
    return (a + b) / 2.0

def visible_enough(visList, threshold=0.6):
    return all(v is not None and v >= threshold for v in visList)
