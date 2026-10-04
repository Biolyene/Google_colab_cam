import base64
import time
import cv2
import numpy as np
from IPython.display import display, Image
from google.colab.output import eval_js

# 用于保存各个窗口的 display handle
_DISPLAY_HANDLES = {}
_ACTIVE_CAPTURE = None

class ColabVideoCapture:
    """
    无缝接管 cv2.VideoCapture
    index = 0: 默认前置镜头 (user)
    index = 1: 默认后置镜头 (environment)
    """
    def __init__(self, index=0, width=360, quality=0.4):
        global _ACTIVE_CAPTURE
        self.facing_mode = 'environment' if index == 1 else 'user'
        self.width = width
        self.quality = quality
        self.is_opened = False
        _ACTIVE_CAPTURE = self
        self._start_stream()

    def _start_stream(self):
        js_init = f'''
        (async () => {{
            if (window.videoStream) {{
                window.videoStream.getTracks().forEach(t => t.stop());
            }}
            if (window.streamDiv) window.streamDiv.remove();

            window.streamDiv = document.createElement('div');
            window.streamDiv.style.marginBottom = '8px';

            window.btnStop = document.createElement('button');
            window.btnStop.textContent = '⏹ 停止 (退出 cv2 循环)';
            window.btnStop.style.padding = '6px 12px';
            window.btnStop.style.backgroundColor = '#d93025';
            window.btnStop.style.color = 'white';
            window.btnStop.style.border = 'none';
            window.btnStop.style.borderRadius = '4px';
            window.btnStop.style.cursor = 'pointer';

            window.videoEl = document.createElement('video');
            window.videoEl.style.display = 'none';
            window.videoEl.playsInline = true;
            window.videoEl.autoplay = true;

            window.streamDiv.appendChild(window.btnStop);
            window.streamDiv.appendChild(window.videoEl);
            document.body.appendChild(window.streamDiv);

            window.videoStream = await navigator.mediaDevices.getUserMedia({{
                video: {{ facingMode: {{ ideal: "{self.facing_mode}" }} }}
            }});
            window.videoEl.srcObject = window.videoStream;
            await window.videoEl.play();

            window.isStreaming = true;
            window.btnStop.onclick = () => {{ window.isStreaming = false; }};

            const scale = {self.width} / window.videoEl.videoWidth;
            window.captureCanvas = document.createElement('canvas');
            window.captureCanvas.width = {self.width};
            window.captureCanvas.height = Math.round(window.videoEl.videoHeight * scale);
            window.captureCtx = window.captureCanvas.getContext('2d', {{ willReadFrequently: true }});
            return "SUCCESS";
        }})()
        '''
        try:
            res = eval_js(js_init)
            self.is_opened = (res == "SUCCESS")
        except Exception as e:
            print(f"摄像头启动失败: {e}")
            self.is_opened = False

    def isOpened(self):
        return self.is_opened

    def read(self):
        if not self.is_opened:
            return False, None
        
        js_capture = f'''
        (() => {{
            if (!window.isStreaming || !window.videoStream) return "STOP";
            window.captureCtx.drawImage(window.videoEl, 0, 0, window.captureCanvas.width, window.captureCanvas.height);
            return window.captureCanvas.toDataURL('image/jpeg', {self.quality});
        }})()
        '''
        try:
            data = eval_js(js_capture)
            if data == "STOP" or not data:
                return False, None
            
            binary = base64.b64decode(data.split(',')[1])
            frame = cv2.imdecode(np.frombuffer(binary, dtype=np.uint8), cv2.IMREAD_COLOR)
            return True, frame
        except Exception:
            return False, None

    def release(self):
        self.is_opened = False
        js_clean = '''
        (() => {
            if (window.videoStream) {
                window.videoStream.getTracks().forEach(t => t.stop());
                window.videoStream = null;
            }
            if (window.streamDiv) window.streamDiv.remove();
        })()
        '''
        try:
            eval_js(js_clean)
        except Exception:
            pass


def _colab_imshow(winname, mat):
    """接管 cv2.imshow，实现原地无闪烁刷新"""
    global _DISPLAY_HANDLES
    if winname not in _DISPLAY_HANDLES:
        _DISPLAY_HANDLES[winname] = display(None, display_id=True)
    
    # 编码为 JPEG 回传显示
    success, buffer = cv2.imencode('.jpg', mat, [cv2.IMWRITE_JPEG_QUALITY, 55])
    if success:
        _DISPLAY_HANDLES[winname].update(Image(data=buffer.tobytes()))


def _colab_waitKey(delay=1):
    """
    接管 cv2.waitKey
    如果用户在网页上点了【⏹ 停止】，模拟返回 ord('q') 触发原生循环退出
    """
    global _ACTIVE_CAPTURE
    if _ACTIVE_CAPTURE and not _ACTIVE_CAPTURE.is_opened:
        return ord('q')
    
    try:
        is_running = eval_js('window.isStreaming === true')
        if not is_running:
            return ord('q')
    except Exception:
        return ord('q')
    
    return -1


def _colab_destroyAllWindows():
    """接管 cv2.destroyAllWindows"""
    global _DISPLAY_HANDLES, _ACTIVE_CAPTURE
    _DISPLAY_HANDLES.clear()
    if _ACTIVE_CAPTURE:
        _ACTIVE_CAPTURE.release()


# ===================================================
# 核心魔法：自动将系统原生 cv2 替换为我们的 Colab 适配器
# ===================================================
cv2.VideoCapture = ColabVideoCapture
cv2.imshow = _colab_imshow
cv2.waitKey = _colab_waitKey
cv2.destroyAllWindows = _colab_destroyAllWindows

print("✅ 已成功为 OpenCV 注入 Google Colab / 平板摄像头补丁！")