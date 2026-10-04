# 📷 Google_colab_cam

> **让 OpenCV 的本地摄像头代码在 Google Colab 上无缝运行！**  
> 专为平板（iPad / Android）与电脑浏览器设计，完全兼容原生 OpenCV API。

---

## 💡 为什么需要这个库？

在 Google Colab 中运行 OpenCV 时，通常会遇到以下问题：
1. **无法读取本地摄像头**：Colab 运行在远程云端服务器上，调用 `cv2.VideoCapture(0)` 会因找不到物理机房摄像头而报错或黑屏。
2. **`cv2.imshow()` 被禁用**：由于云端服务器没有桌面 GUI 环境，调用 `cv2.imshow()` 会直接抛出 `DisabledFunctionError`。

**`Google_colab_cam`** 通过热补丁（Monkey Patch）无缝接管了底层调用，借助浏览器的 WebRTC 将平板/电脑的本地摄像头画面传输给 Python。**你无需重写或大幅改造 OpenCV 代码，就能获得像在本地电脑上一样的开发体验！**

___

## 📦 安装方法

在 Google Colab 的单元格中运行以下命令安装：

```bash
!pip install --upgrade git+https://github.com/Biolyene/Google_colab_cam.git

```

## 🚀 快速上手
安装完成后，只需在代码最开头加入 import colabcam，剩下的代码完全按照教科书上标准的 OpenCV 语法书写即可：
```code
import colabcam  # 👈 导入本库即可自动注入 OpenCV 补丁！
import cv2

# 初始化摄像头：0 为前置摄像头，1 为后置摄像头
cap = cv2.VideoCapture(0)

print("正在启动摄像头并运行 OpenCV 循环...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # ------------------------------------------------
    # 可以在这里编写任意标准的 OpenCV 图像处理逻辑：
    # ------------------------------------------------
    frame = cv2.flip(frame, 1)                  # 画面镜像翻转
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 转为灰度图
    edges = cv2.Canny(gray, 100, 200)           # 边缘检测

    # 原生 imshow：画面将在 Colab 单元格内原地无闪烁流畅刷新！
    cv2.imshow('Camera Live Feed', edges)

    # 监听退出：点击页面上的【⏹ 停止】按钮会自动触发 ord('q') 优雅退出
    if cv2.waitKey(1) == ord('q'):
        break

# 释放摄像头资源
cap.release()
cv2.destroyAllWindows()
print("摄像头已安全释放，处理结束。")

```
___
## 🌟 核心特性:

### ✨ 零学习成本：无需使用繁琐的 JavaScript 嵌入代码，继续使用 VideoCapture、read()、imshow() 与 waitKey()。
### 📱 完美适配移动端与平板: 
完美支持 iPad（Safari）及 Android 平板。
内置 playsinline 适配，解决移动端浏览器全屏或无法内联播放的问题。
### 🔄 前后置镜头轻松切换: 
cv2.VideoCapture(0) ➔ 默认调用前置/自拍镜头。
cv2.VideoCapture(1) ➔ 默认调用后置镜头（适合平板扫描、拍摄外部环境）。
### ⏹ 友好的交互式停止按钮: 
自动在视频预览区上方注入一个红色的 ⏹ 停止 按钮。
点击按钮后，后端的 cv2.waitKey() 会自动接收到退出信号并打破 while 循环，彻底告别必须手动中断内核的尴尬。
### ⚡ 低延迟与防闪烁: 
采用 Jupyter 专属的 DisplayHandle 进行增量刷新，告别 clear_output() 带来的严重闪屏。
### ⚙️ 参数与镜头映射: 
代码调用	对应镜头	适用场景
cv2.VideoCapture(0)	前置镜头 (User / Selfie)	人脸识别、表情分析、手势追踪
cv2.VideoCapture(1)	后置镜头 (Environment)	平板拍摄书本、物体检测、OCR 文字识别
___
## ⚠️ 常见问题排查 (FAQ)
Q1：运行单元格后报错 NotReadableError: Could not start video source？
* 原因：平板操作系统对摄像头独占要求极高。如果上一次运行未正常退出，或后台有其他 App（微信、相机等）占用了摄像头，系统就会拒绝访问。
解决办法：直接刷新一下当前 Google Colab 的网页标签页（Refresh），即可强制释放被占用的摄像头硬件。
Q2：为什么画面看起来比电脑端略有延迟？
* 说明：因为视频帧需要经历 平板端抓拍 ➔ 网络传输至 Google 云端机房 ➔ OpenCV 处理 ➔ 传回平板 的过程。为了保证在平板网络下的流畅度，本库已自动将流媒体传输分辨率与压缩比优化到最佳平衡点。
___
## 📄 开源许可
本项目基于 MIT License 开源。欢迎提交 PR 和 Issue！


