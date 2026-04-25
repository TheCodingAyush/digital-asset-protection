import os
import requests
from PIL import Image

# Configuration
IMAGE_PATH = 'test_image.jpg'
UPLOAD_URL = 'http://localhost:8000/upload/image'
DATASET_ADD_URL = 'http://localhost:8000/dataset/add'

def main():
    # 1. Create a dummy image if it doesn't exist
    if not os.path.exists(IMAGE_PATH):
        print(f"[*] Creating dummy {IMAGE_PATH}...")
        img = Image.new('RGB', (100, 100), color='red')
        img.save(IMAGE_PATH)

    # 2. Upload image to get phash and embedding
    print(f"[*] Uploading {IMAGE_PATH} to {UPLOAD_URL}...")
    try:
        with open(IMAGE_PATH, 'rb') as f:
            files = {'file': (IMAGE_PATH, f, 'image/jpeg')}
            upload_res = requests.post(UPLOAD_URL, files=files)
            
        if not upload_res.ok:
            print(f"[!] Upload failed with status {upload_res.status_code}: {upload_res.text}")
            return
            
        upload_data = upload_res.json()
        frames = upload_data.get('frames', [])
        
        if not frames:
            print("[!] No frames returned in upload response.")
            return
            
        first_frame = frames[0]
        phash = first_frame.get('phash')
        embedding = first_frame.get('embedding')
        
        if not phash or not embedding:
            print("[!] Missing phash or embedding in response.")
            return
            
        print("[*] Successfully extracted phash and embedding.")
        print(f"[*] pHash: {phash}")
        print(f"[*] Embedding (first 5 values): {embedding[:5]}")
        print(f"[*] Full embedding saved to: backend/test_embedding.json")

        import json
        with open("test_embedding.json", "w") as f:
            json.dump({"phash": phash, "embedding": embedding}, f)
        
    except Exception as e:
        print(f"[!] Error during upload: {e}")
        return

    # 3. Add to dataset
    payload = {
        "id": "ref-001",
        "title": "Original Test Image",
        "url": "https://example.com",
        "source": "FrameLens Test",
        "phash": phash,
        "embedding": embedding
    }

    print(f"[*] Adding to dataset via {DATASET_ADD_URL}...")
    try:
        add_res = requests.post(DATASET_ADD_URL, json=payload)
        if add_res.ok:
            print(f"[+] Success! Dataset added: {add_res.json()}")
        else:
            print(f"[!] Dataset add failed with status {add_res.status_code}: {add_res.text}")
    except Exception as e:
        print(f"[!] Error adding to dataset: {e}")

if __name__ == '__main__':
    main()
