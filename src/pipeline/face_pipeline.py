import dlib
import numpy as np
import face_recognition_models
from jsonschema.exceptions import best_match
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students

@st.cache_resource
def load_dlib_models():
    """Load dlib's face recognition models."""
    # Load the face detector
    detector = dlib.get_frontal_face_detector()

    # Load the shape predictor for facial landmarks
    #shape_predictor
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    # Load the face recognition model
    facerec = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())

    return detector, sp, facerec

def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces  = detector(image_np, 1)

    encodings=[]

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1) #128 embedding

        encodings.append(np.array(face_descriptor))

    return encodings

def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get("face_embedding")
        if embedding:
            X.append(embedding)
            y.append(student["student_id"])

    if len(X) == 0:
        return None

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        clf.fit(X, y)
    except ValueError:
        pass

    return {'clf':clf, 'X':X, 'y':y}

def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_students = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_students, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[y_train.index(predicted_id)]

        best_match_score = np.linalg.norm(
            #student_embedding - encoding
            np.array(student_embedding) - np.array(encoding)
        )

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:
            detected_students[predicted_id] = True
    return detected_students, all_students, len(encodings)