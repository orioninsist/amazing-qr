
import os
from PIL import Image

def analyze_assets(directory):
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    analysis = []
    
    for file in files:
        path = os.path.join(directory, file)
        size_kb = os.path.getsize(path) / 1024
        
        with Image.open(path) as img:
            width, height = img.size
            mode = img.mode
            format = img.format
            is_animated = getattr(img, "is_animated", False)
            
        analysis.append({
            "name": file,
            "size_kb": size_kb,
            "resolution": f"{width}x{height}",
            "format": format,
            "is_animated": is_animated
        })
    
    return analysis

if __name__ == "__main__":
    assets_dir = "/mnt/samsung/orion-backup-local/projects/amazing-qr/portfolio/assets"
    results = analyze_assets(assets_dir)
    
    print("| File Name | Size (KB/MB) | Resolution | Format | Type |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    for r in results:
        size_str = f"{r['size_kb']:.2f} KB" if r['size_kb'] < 1024 else f"{r['size_kb']/1024:.2f} MB"
        type_str = "Animated" if r['is_animated'] else "Static"
        print(f"| {r['name']} | {size_str} | {r['resolution']} | {r['format']} | {type_str} |")
