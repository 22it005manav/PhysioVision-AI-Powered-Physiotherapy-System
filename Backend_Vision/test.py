# import cv2
# import mediapipe as mp

# def test_mediapipe():
#     try:
#         # Initialize MediaPipe Face Detection
#         mp_face_detection = mp.solutions.face_detection
#         mp_drawing = mp.solutions.drawing_utils

#         cap = cv2.VideoCapture(0)

#         with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
#             while cap.isOpened():
#                 success, image = cap.read()
#                 if not success:
#                     print("Ignoring empty camera frame.")
#                     break

#                 # Convert the BGR image to RGB
#                 image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#                 # Process the image
#                 results = face_detection.process(image_rgb)

#                 # Draw face detections
#                 if results.detections:
#                     for detection in results.detections:
#                         mp_drawing.draw_detection(image, detection)

#                 cv2.imshow('MediaPipe Test - Press Q to exit', image)

#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break

#         cap.release()
#         cv2.destroyAllWindows()
#         print("✅ MediaPipe is working correctly!")

#     except ImportError:
#         print("❌ MediaPipe is NOT installed.")
#     except Exception as e:
#         print("⚠️ MediaPipe installed but error occurred:", e)

# if __name__ == "__main__":
#     test_mediapipe()


import tensorflow as tf
print(tf)
print(tf.__file__)