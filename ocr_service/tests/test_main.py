# ocr_service/tests/test_main.py

def test_health_check(client):
    """Test the health check endpoint"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"

def test_extract_success(client, img_bytes):
    """Test successful OCR extraction from image"""
    resp = client.post(
        "/extract",
        files={"file": ("test.png", img_bytes, "image/png")}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Check required fields
    assert "text" in data
    assert "filename" in data
    assert "file_type" in data
    assert "status" in data

    # Check data types and values
    assert isinstance(data["text"], str)
    assert data["filename"] == "test.png"
    assert data["file_type"] == "image"
    assert data["status"] == "success"
    assert data["text"] == "texte factice OCR"  # Our mocked response

def test_extract_bad_format(client):
    """Test rejection of unsupported file format"""
    resp = client.post(
        "/extract",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert resp.status_code == 415
    data = resp.json()
    assert "detail" in data
    assert "Format non supporté" in data["detail"]
