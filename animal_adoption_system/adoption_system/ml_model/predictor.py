import pickle
import os


# ==============================
# LOAD MODEL AND VECTORIZER
# ==============================

BASE_DIR = os.path.dirname(__file__)

model_path = os.path.join(BASE_DIR, "disease_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))


# ==============================
# DISEASE PREDICTION FUNCTION
# ==============================

def predict_disease(symptoms_text):
    """
    Takes symptom text and returns
    top 3 predicted diseases with confidence %
    """

    if not symptoms_text:
        return []

    # convert symptoms into vector
    symptoms_vector = vectorizer.transform([symptoms_text])

    # get probabilities for all diseases
    probabilities = model.predict_proba(symptoms_vector)[0]
    diseases = model.classes_

    # pair disease with probability
    disease_prob_pairs = list(zip(diseases, probabilities))

    # sort by highest probability
    disease_prob_pairs.sort(key=lambda x: x[1], reverse=True)

    # take top 3 predictions
    top3 = disease_prob_pairs[:3]

    # convert to percentage
    results = [
        (disease, round(prob * 100, 2))
        for disease, prob in top3
    ]

    return results
