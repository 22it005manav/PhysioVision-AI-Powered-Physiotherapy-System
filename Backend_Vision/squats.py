import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.preprocessing import StandardScaler, LabelEncoder
import cv2
import tensorflow as tf
import os
import asyncio
import json
from collections import deque
import time
import joblib
import logging
import mediapipe as mp
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SquatAnalyzer:
    def __init__(self):
        base_dir = os.path.dirname(__file__)

        # ✅ Correct paths
        self.model_path = os.path.join(base_dir, "models_vision", "best_squat_model.keras")
        self.scaler_path = os.path.join(base_dir, "models_vision", "preprocessed_data_scaler.joblib")
        self.label_encoder_path = os.path.join(base_dir, "models_vision", "preprocessed_data_label_encoder.joblib")

        print("🔥 Model path:", self.model_path)

        # ✅ Default config
        self.window_size = 30

        # Buffers
        self.features_buffer = deque(maxlen=self.window_size)
        self.last_predictions = deque(maxlen=5)

        # State
        self.current_prediction = None
        self.prediction_confidence = 0.0
        self.rep_count = 0

        # Load model safely
        try:
            if os.path.exists(self.model_path):
                print("🧠 Loading model...")
                self.model = tf.keras.models.load_model(self.model_path, compile=False)
            else:
                print("⚠️ Model not found")
                self.model = None

            self.scaler = joblib.load(self.scaler_path) if os.path.exists(self.scaler_path) else None
            self.label_encoder = joblib.load(self.label_encoder_path) if os.path.exists(self.label_encoder_path) else None

            print("✅ Initialization complete")
        except Exception as e:
            print("❌ Error loading model:", e)
            self.model = None
            self.scaler = None
            self.label_encoder = None

        # MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
)

        # ✅ ADD THESE (IMPORTANT)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def _encode_frame(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')

    def _process_frame(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if not results.pose_landmarks:
            return None, frame

        annotated_frame = frame.copy()

        # ✅ FIXED DRAWING (compatible with all versions)
        self.mp_drawing.draw_landmarks(
            annotated_frame,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            # ❌ removed connection style
        )

        dummy_features = np.zeros(20)

        return dummy_features, annotated_frame

    def _make_prediction(self):
        if self.model is None or self.scaler is None or self.label_encoder is None:
            return None, 0.0

        try:
            data = np.array(self.features_buffer)
            data = self.scaler.transform(data)
            data = data.reshape(1, self.window_size, -1)

            pred = self.model.predict(data)[0]
            idx = np.argmax(pred)

            return self.label_encoder.classes_[idx], float(pred[idx])
        except Exception as e:
            print("Prediction error:", e)
            return None, 0.0

    async def process_video(self, frame):
        features, annotated = self._process_frame(frame)

        if features is None:
            return {
                "type": "frame",
                "data": self._encode_frame(frame)
            }

        self.features_buffer.append(features)

        if len(self.features_buffer) == self.window_size:
            pred, conf = self._make_prediction()
            self.current_prediction = pred
            self.prediction_confidence = conf

        return {
            "type": "frame",
            "data": self._encode_frame(annotated),
            "prediction": self.current_prediction,
            "confidence": self.prediction_confidence,
            "rep_count": self.rep_count
        }

    def reset_counters(self):
        self.rep_count = 0
        self.features_buffer.clear()
        print("Counters reset")
