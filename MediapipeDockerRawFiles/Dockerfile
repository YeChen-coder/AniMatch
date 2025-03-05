# 使用 AWS 官方的 Python 3.9 Lambda 运行时基础镜像
FROM public.ecr.aws/lambda/python:3.9

# 1) 安装系统库，让容器里有 libGL.so.1
RUN yum install -y mesa-libGL

# 安装依赖
# - mediapipe, opencv-python-headless, numpy, Pillow 等
RUN pip install --no-cache-dir mediapipe opencv-python-headless numpy Pillow

# (可选) 如果你还要 PyTorch/TensorFlow:
# RUN pip install --no-cache-dir torch torchvision
# RUN pip install --no-cache-dir tensorflow

# 将你的模型文件复制进容器(如果你本地有 face_landmarker_v2_with_blendshapes.task)
COPY face_landmarker_v2_with_blendshapes.task /var/task/

# 将 app.py 复制进容器
COPY app.py /var/task

# 告诉 Lambda 入口函数是 app.lambda_handler
CMD ["app.lambda_handler"]
