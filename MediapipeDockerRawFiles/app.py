import json
import base64
import io
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
from PIL import Image

# -------------------------
# 1) 初始化 FaceLandmarker
# -------------------------
# 假设你把模型文件 face_landmarker_v2_with_blendshapes.task 放在同一目录
# 如果你没放在同目录，就改一下 model_asset_path 的路径。
base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)


# -------------------------
# 2) 计算 mouthOpen
# -------------------------
def calculate_mouth_open(landmarks):
    """
    计算 mouthOpen 的值。
    :param landmarks: Mediapipe FaceMesh landmarks (x, y, z)。
    :return: 标准化的 mouthOpen 值。
    """
    # 下列索引根据官方FaceMesh定义
    upper_lip_idx = 13
    lower_lip_idx = 14
    left_mouth_corner_idx = 78
    right_mouth_corner_idx = 308

    upper_lip = landmarks[upper_lip_idx]
    lower_lip = landmarks[lower_lip_idx]
    left_mouth_corner = landmarks[left_mouth_corner_idx]
    right_mouth_corner = landmarks[right_mouth_corner_idx]

    # 计算垂直距离
    vertical_distance = abs(lower_lip.y - upper_lip.y)
    # 计算水平距离(嘴巴宽)
    horizontal_width = abs(right_mouth_corner.x - left_mouth_corner.x)

    if horizontal_width == 0:
        return 0.0

    mouth_open = vertical_distance / horizontal_width
    return mouth_open


# -------------------------
# 3) 筛选感兴趣的 blendshapes
# -------------------------
def extract_calculable_blendshapes(blendshapes_list):
    """
    从 Mediapipe 输出的 face_blendshapes 中，筛选感兴趣的项目并返回它们的分数。
    :param blendshapes_list: detection_result.face_blendshapes[0]，每个元素包含 category_name / score
    :return: dict：包含 blendshapes_name: score
    """
    # 你想要对比或计算的 blendshapes
    calculable_blendshapes = [
        "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
        "eyeBlinkLeft", "eyeBlinkRight", "mouthSmileLeft", "mouthSmileRight",
        "mouthClose", "noseSneerLeft", "noseSneerRight"
    ]

    filtered_blendshapes = {}
    for category in blendshapes_list:
        if category.category_name in calculable_blendshapes:
            filtered_blendshapes[category.category_name] = category.score
    return filtered_blendshapes


# -------------------------
# 4) 核心检测函数
# -------------------------
def detect_face_and_calculate_features(image_data_bytes):
    """
    给定一张人脸图片（bytes 数据），返回 mouthOpen 和感兴趣的 blendshapes。
    :param image_data_bytes: 图片的二进制数据
    :return: (mouthOpen值, blendshapes字典)
    """
    # 读取为 PIL
    pil_img = Image.open(io.BytesIO(image_data_bytes)).convert("RGB")
    # 转为 Mediapipe Image
    rgb_array = np.array(pil_img)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_array)

    # 检测
    detection_result = detector.detect(mp_image)
    if not detection_result.face_landmarks:
        return 0.0, {}

    # 第一个人脸
    face_landmarks = detection_result.face_landmarks[0]
    mouth_open_val = calculate_mouth_open(face_landmarks)

    # blendshapes
    if detection_result.face_blendshapes:
        blendshapes_dict = extract_calculable_blendshapes(detection_result.face_blendshapes[0])
    else:
        blendshapes_dict = {}

    # 可把 mouthOpen 放进 blendshapes
    blendshapes_dict['mouthOpen'] = mouth_open_val

    return mouth_open_val, blendshapes_dict


# -------------------------
# 5) Lambda 入口函数
# -------------------------
def lambda_handler(event, context):
    """
    Lambda 调用入口。
    event 里应该包含: event["body"] = '{"image_base64":"xxxx"}'
    """
    try:
        body = json.loads(event.get("body", "{}"))
        image_b64 = body.get("image_base64")
        if not image_b64:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No image_base64 found in request body."})
            }

        # 1) 解码 base64
        image_data = base64.b64decode(image_b64)

        # 2) 检测
        mouth_open_val, blendshapes = detect_face_and_calculate_features(image_data)

        # 3) 返回结果
        return {
            "statusCode": 200,
            "body": json.dumps({
                "mouthOpen": mouth_open_val,
                "blendshapes": blendshapes
            }),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }


# -------------------------
# 6) (可选) 本地测试入口
# -------------------------
if __name__ == "__main__":
    # 在本地做简单测试(非 Lambda 运行环境)
    test_image_path = "HumanOpenmouth.png"  # 你本地的一张人脸图
    with open(test_image_path, "rb") as f:
        img_bytes = f.read()

    mo_val, bshapes = detect_face_and_calculate_features(img_bytes)
    print("MouthOpen:", mo_val)
    print("Blendshapes:", bshapes)
