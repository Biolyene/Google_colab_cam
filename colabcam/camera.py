import base64
import cv2
import numpy as np

try:
    from google.colab.output import eval_js
except ImportError:
    eval_js = None


def capture(default_facing="user", quality=0.85):
    """
    调起平板/电脑浏览器摄像头并截取一帧。
    
    :param default_facing: 默认优先选中的镜头，'user' 为前置/自拍镜头，'environment' 为后置镜头
    :param quality: 传输图像质量 (0.1 ~ 1.0)
    :return: frame (np.ndarray - OpenCV BGR 格式) 或 None (取消或失败)
    """
    if eval_js is None:
        raise EnvironmentError("当前环境未检测到 Google Colab，该库专为 Colab 环境设计。")

    js_code = f'''
    (async () => {{
        const div = document.createElement('div');
        div.style.padding = '12px';
        div.style.background = '#f1f3f4';
        div.style.borderRadius = '8px';
        div.style.display = 'inline-block';
        div.style.boxShadow = '0 1px 3px rgba(0,0,0,0.12)';

        // 镜头下拉选择器
        const select = document.createElement('select');
        select.style.padding = '6px 10px';
        select.style.marginRight = '8px';
        select.style.fontSize = '14px';
        select.style.borderRadius = '4px';

        // 拍照按钮
        const btnSnap = document.createElement('button');
        btnSnap.textContent = '📸 拍照并传输';
        btnSnap.style.padding = '6px 14px';
        btnSnap.style.fontSize = '14px';
        btnSnap.style.backgroundColor = '#1a73e8';
        btnSnap.style.color = 'white';
        btnSnap.style.border = 'none';
        btnSnap.style.borderRadius = '4px';
        btnSnap.style.cursor = 'pointer';

        // 取消按钮
        const btnCancel = document.createElement('button');
        btnCancel.textContent = '✖ 取消';
        btnCancel.style.marginLeft = '8px';
        btnCancel.style.padding = '6px 12px';
        btnCancel.style.fontSize = '14px';
        btnCancel.style.backgroundColor = '#dadce0';
        btnCancel.style.color = '#3c4043';
        btnCancel.style.border = 'none';
        btnCancel.style.borderRadius = '4px';
        btnCancel.style.cursor = 'pointer';

        // 视频画面
        const video = document.createElement('video');
        video.style.display = 'block';
        video.style.marginTop = '10px';
        video.style.maxWidth = '100%';
        video.style.maxHeight = '420px';
        video.style.borderRadius = '6px';
        video.playsInline = true;
        video.autoplay = true;

        div.appendChild(select);
        div.appendChild(btnSnap);
        div.appendChild(btnCancel);
        div.appendChild(video);
        document.body.appendChild(div);

        let currentStream = null;

        function stopTracks() {{
            if (currentStream) {{
                currentStream.getTracks().forEach(t => t.stop());
            }}
        }}

        async function startCamera(deviceId) {{
            stopTracks();
            try {{
                const constraints = {{
                    video: deviceId ? {{ deviceId: {{ exact: deviceId }} }} : {{ facingMode: {{ ideal: "{default_facing}" }} }}
                }};
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
            }} catch (err) {{
                console.error("启动摄像头错误:", err);
            }}
        }}

        // 预检权限并枚举平板设备的所有摄像头
        await navigator.mediaDevices.getUserMedia({{ video: true }});
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');

        select.innerHTML = '';
        videoDevices.forEach((dev, idx) => {{
            const opt = document.createElement('option');
            opt.value = dev.deviceId;
            opt.text = dev.label || `摄像头 ${{idx + 1}}`;
            select.appendChild(opt);
        }});

        await startCamera(videoDevices[0]?.deviceId);

        select.onchange = () => startCamera(select.value);

        // 等待拍照或取消
        const action = await new Promise((resolve) => {{
            btnSnap.onclick = () => resolve('capture');
            btnCancel.onclick = () => resolve('cancel');
        }});

        if (action === 'cancel') {{
            stopTracks();
            div.remove();
            return '';
        }}

        // 截帧
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);

        stopTracks();
        div.remove();

        return canvas.toDataURL('image/jpeg', {quality});
    }})()
    '''

    try:
        data = eval_js(js_code)
        if not data:
            return None
        binary = base64.b64decode(data.split(',')[1])
        img_array = np.frombuffer(binary, dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"摄像头读取异常: {e}")
        return None


class VideoCapture:
    """
    仿照 cv2.VideoCapture 的封装类
    """
    def __init__(self, camera_type="user", quality=0.85):
        self.camera_type = camera_type
        self.quality = quality

    def read(self):
        """
        模拟 cv2.VideoCapture().read() -> (ret, frame)
        """
        frame = capture(default_facing=self.camera_type, quality=self.quality)
        if frame is not None:
            return True, frame
        return False, None

    def release(self):
        pass