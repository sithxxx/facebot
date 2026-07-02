import cv2
import mediapipe as mp
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def debug_landmarks(image_path: str):
    img = cv2.imread(image_path)
    if img is None:
        print("Ошибка: не удалось прочитать изображение")
        return
    h, w = img.shape[:2]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "..", "face_analysis", "face_landmarker.task")
    
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False
    )
    
    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        results = landmarker.detect(mp_image)
        
        if not results.face_landmarks:
            print("Лицо не найдено")
            return
        
        lm = results.face_landmarks[0]
        
        key_points = {
            "left_jaw": 172,
            "right_jaw": 397,
            "chin": 152,
            "left_brow_inner": 107,
            "right_brow_inner": 336,
            "left_eye_top": 159,
            "right_eye_top": 386,
        }
        
        for name, idx in key_points.items():
            x = int(lm[idx].x * w)
            y = int(lm[idx].y * h)
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(img, name, (x+5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
        
        cv2.imwrite("debug_landmarks.jpg", img)
        print("Сохранено: debug_landmarks.jpg")

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "test_photo.jpeg")
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
    else:
        debug_landmarks(image_path)
