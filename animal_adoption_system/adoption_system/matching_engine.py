from datetime import timedelta
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import FoundPet

# ================= RULE + ML MATCHING =================

def build_feature_vector_lost(lost_pet):
    return [
        len(lost_pet.breed or ""),
        len(lost_pet.identification_details or "")
    ]

def build_feature_vector_found(found_pet):
    return [
        len(found_pet.description or ""),
        len(found_pet.condition or "")
    ]

def calculate_similarity(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]

def find_best_match(lost_pet):
    candidates = FoundPet.objects.filter(
        pet_type=lost_pet.pet_type,
        status="Found",
        date_found__range=(
            lost_pet.date_lost - timedelta(days=7),
            lost_pet.date_lost + timedelta(days=7)
        )
    )

    best_match = None
    highest_score = 0

    for found_pet in candidates:
        lost_vec = build_feature_vector_lost(lost_pet)
        found_vec = build_feature_vector_found(found_pet)

        score = calculate_similarity(lost_vec, found_vec)

        if score > highest_score:
            highest_score = score
            best_match = found_pet

    return best_match, highest_score


# ================= IMAGE MATCHING =================

from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image

base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = base_model.predict(img_array)
    return features

def image_similarity(img1, img2):
    try:
        f1 = extract_features(img1.path)
        f2 = extract_features(img2.path)
        return cosine_similarity(f1, f2)[0][0]
    except:
        return 0