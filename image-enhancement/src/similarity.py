from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import cv2

def cosine_similarity_score(vec1, vec2):

    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)

    similarity = cosine_similarity(vec1, vec2)

    return similarity[0][0]





def save_comparison_image(before, after, save_path):

    before = cv2.resize(before, (300, 300))
    after = cv2.resize(after, (300, 300))

    combined = np.hstack((before, after))

    cv2.putText(combined, "before",(50, 30), cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),2)

    cv2.putText(combined,"after",(350, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imwrite(save_path, combined)