# Google_colab_cam
允许用户在google colab上打开摄像头，兼容opencv

安装方法：
'''
!pip install git+https://github.com/Biolyene/Google_colab_cam.git
'''

在google colab里的cell先填入以上的命令，接着可以参考一下的程序
'''
import colabcam  # 👈 加上这行即可！
import cv2

# 0 代表前置摄像头，1 代表后置摄像头
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # ------------------------------------
    # 原生 OpenCV 逻辑：直接写，无需改动
    # ------------------------------------
    frame = cv2.flip(frame, 1)  # 镜像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # 像普通电脑一样直接 imshow！
    cv2.imshow('Camera Feed', edges)

    # 像普通电脑一样 waitKey 检测 'q' 键退出
    if cv2.waitKey(1) == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
print("视频处理完成！")

'''