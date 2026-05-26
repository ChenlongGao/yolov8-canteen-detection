"""
MediaPipe 算法服务模块
- 人脸检测 (MediaPipe FaceDetector + OpenCV Haar 备选)
- 手部关键点 (MediaPipe HandLandmarker)
- 姿态关键点 (MediaPipe PoseLandmarker) 
- 人脸网格 (MediaPipe FaceLandmarker)
"""
import os
import cv2
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mediapipe_models")

# ========== 模型管理 ==========
_mp_models = {}

def _get_model_path(name):
    """获取模型文件路径，不存在则返回 None"""
    path = os.path.join(MODELS_DIR, name)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    return None

def _ensure_models():
    """确保模型目录存在"""
    os.makedirs(MODELS_DIR, exist_ok=True)

_ensure_models()

# ========== 人脸检测 ==========
def detect_faces(image_bgr, min_confidence=0.5):
    """
    人脸检测：优先 MediaPipe FaceDetector，降级 OpenCV Haar Cascade
    返回: [{"bbox": [x1,y1,x2,y2], "confidence": 0.9, "keypoints": {...}}, ...]
    """
    results = []
    
    # 方案1: MediaPipe FaceDetector
    model_path = _get_model_path("face_detector_short.tflite")
    if model_path:
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import vision
            BaseOptions = mp.tasks.BaseOptions
            FaceDetector = vision.FaceDetector
            FaceDetectorOptions = vision.FaceDetectorOptions
            
            options = FaceDetectorOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                min_detection_confidence=min_confidence,
                running_mode=mp.tasks.vision.RunningMode.IMAGE
            )
            detector = FaceDetector.create_from_options(options)
            
            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            detection_result = detector.detect(mp_image)
            detector.close()
            
            for det in detection_result.detections:
                bbox = det.bounding_box
                results.append({
                    "bbox": [bbox.origin_x, bbox.origin_y,
                             bbox.origin_x + bbox.width, bbox.origin_y + bbox.height],
                    "confidence": round(det.categories[0].score, 3),
                    "keypoints": {
                        "left_eye": (det.keypoints[0].x, det.keypoints[0].y) if det.keypoints else None,
                        "right_eye": (det.keypoints[1].x, det.keypoints[1].y) if det.keypoints else None,
                        "nose": (det.keypoints[2].x, det.keypoints[2].y) if det.keypoints else None,
                        "mouth": (det.keypoints[3].x, det.keypoints[3].y) if det.keypoints else None,
                        "left_ear": (det.keypoints[4].x, det.keypoints[4].y) if det.keypoints else None,
                        "right_ear": (det.keypoints[5].x, det.keypoints[5].y) if det.keypoints else None,
                    }
                })
            if results:
                return results
        except Exception as e:
            pass  # MediaPipe failed, fall back to OpenCV
    
    # 方案2: OpenCV Haar Cascade (备选)
    try:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            results.append({
                "bbox": [int(x), int(y), int(x + w), int(y + h)],
                "confidence": 0.8,
                "source": "opencv_haar"
            })
    except Exception as e:
        pass
    
    return results


# ========== 手部关键点 ==========
def detect_hands(image_bgr, min_confidence=0.5, max_hands=2):
    """
    手部关键点: MediaPipe HandLandmarker
    返回: [{"handedness": "Left", "landmarks": [[x,y,z], ...], "bbox": [...]}, ...]
    """
    model_path = _get_model_path("hand_landmarker_lite.tflite")
    if not model_path:
        return []
    
    try:
        import mediapipe as mp
        from mediapipe.tasks.python import vision
        
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = vision.HandLandmarker
        HandLandmarkerOptions = vision.HandLandmarkerOptions
        
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_hands=max_hands,
            min_hand_detection_confidence=min_confidence,
            min_hand_presence_confidence=min_confidence,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        detector = HandLandmarker.create_from_options(options)
        
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_image)
        detector.close()
        
        hands = []
        for i, handedness in enumerate(result.handedness):
            category = handedness[0]
            landmarks_list = result.hand_landmarks[i]
            landmarks = [[lm.x, lm.y, lm.z] for lm in landmarks_list]
            
            xs = [lm.x for lm in landmarks_list]
            ys = [lm.y for lm in landmarks_list]
            h, w = image_bgr.shape[:2]
            bbox = [
                int(min(xs) * w), int(min(ys) * h),
                int(max(xs) * w), int(max(ys) * h)
            ]
            
            hands.append({
                "handedness": category.category_name,
                "confidence": round(category.score, 3),
                "bbox": bbox,
                "landmarks_2d": [[int(lm[0] * w), int(lm[1] * h)] for lm in landmarks],
                "landmarks_3d": [[round(lm[0], 4), round(lm[1], 4), round(lm[2], 4)] for lm in landmarks]
            })
        return hands
    except Exception as e:
        return []


# ========== 姿态关键点 ==========
def detect_pose_mp(image_bgr, min_confidence=0.5):
    """
    姿态关键点: MediaPipe PoseLandmarker (33点)
    返回: [{"landmarks_2d": [[x,y],...], "landmarks_3d": [[x,y,z],...], "bbox": [...]}]
    """
    model_path = _get_model_path("pose_landmarker_lite.tflite")
    if not model_path:
        return None
    
    try:
        import mediapipe as mp
        from mediapipe.tasks.python import vision
        
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = vision.PoseLandmarker
        PoseLandmarkerOptions = vision.PoseLandmarkerOptions
        
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            min_pose_detection_confidence=min_confidence,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        detector = PoseLandmarker.create_from_options(options)
        
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_image)
        detector.close()
        
        poses = []
        h, w = image_bgr.shape[:2]
        for landmarks_list in result.pose_landmarks:
            landmarks = [[lm.x, lm.y, lm.z] for lm in landmarks_list]
            xs = [lm.x * w for lm in landmarks_list]
            ys = [lm.y * h for lm in landmarks_list]
            
            poses.append({
                "landmarks_2d": [[int(lm[0] * w), int(lm[1] * h)] for lm in landmarks],
                "landmarks_3d": [[round(lm[0], 4), round(lm[1], 4), round(lm[2], 4)] for lm in landmarks],
                "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
            })
        return poses if poses else None
    except Exception as e:
        return None


# ========== 人脸网格 ==========
def detect_face_mesh(image_bgr, max_faces=1):
    """
    人脸网格: MediaPipe FaceLandmarker (478点)
    返回: [{"landmarks_2d": [[x,y],...], "face_ovals": [[idx,...]], ...}]
    """
    model_path = _get_model_path("face_landmarker.tflite")
    if not model_path:
        return None
    
    try:
        import mediapipe as mp
        from mediapipe.tasks.python import vision
        
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = vision.FaceLandmarker
        FaceLandmarkerOptions = vision.FaceLandmarkerOptions
        
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_faces=max_faces,
            output_face_blendshapes=True,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        detector = FaceLandmarker.create_from_options(options)
        
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_image)
        detector.close()
        
        faces = []
        h, w = image_bgr.shape[:2]
        for i, landmarks_list in enumerate(result.face_landmarks):
            landmarks = [[int(lm.x * w), int(lm.y * h)] for lm in landmarks_list]
            blendshapes = {}
            if result.face_blendshapes:
                for bs in result.face_blendshapes[i]:
                    blendshapes[bs.category_name] = round(bs.score, 3)
            
            xs = [lm[0] for lm in landmarks]
            ys = [lm[1] for lm in landmarks]
            
            faces.append({
                "landmarks_2d": landmarks,
                "blendshapes": blendshapes if blendshapes else None,
                "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
            })
        return faces if faces else None
    except Exception as e:
        return None
