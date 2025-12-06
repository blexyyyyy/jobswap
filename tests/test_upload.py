
import requests
import os

BASE_URL = "http://localhost:8000/api"

def create_mock_pdf():
    with open("test_resume.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Result Test Resume) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000115 00000 n \n0000000257 00000 n \n0000000344 00000 n \ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n438\n%%EOF")

def test_upload():
    if not os.path.exists("test_resume.pdf"):
        create_mock_pdf()

    # 1. Login
    login_data = {
        "email": "test_v2@example.com",
        "password": "password123"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return

        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Upload
        print("Uploading resume...")
        files = {'file': ('test_resume.pdf', open('test_resume.pdf', 'rb'), 'application/pdf')}
        resp = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files=files)
        
        if resp.status_code == 200:
            print(f"Upload Success: {resp.json()}")
        else:
            print(f"Upload Failed: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload()
