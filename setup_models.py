import os
import urllib.request

def download_models():
    model_dir = "models/wechat_qr"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    base_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/wechat_qrcode_20210119/"
    files = [
        "detect.prototxt",
        "detect.caffemodel",
        "sr.prototxt",
        "sr.caffemodel"
    ]

    print(f"🚀 Downloading WeChatQRCode models to {model_dir}...")
    for f in files:
        target_path = os.path.join(model_dir, f)
        if not os.path.exists(target_path):
            url = base_url + f
            print(f"📥 Downloading {f}...")
            try:
                urllib.request.urlretrieve(url, target_path)
                print(f"✅ Saved {f}")
            except Exception as e:
                print(f"❌ Error downloading {f}: {e}")
        else:
            print(f"✅ {f} already exists.")

if __name__ == "__main__":
    download_models()
