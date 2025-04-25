# ocr_service/tests/test_main.py

def test_extract_success(client, img_bytes):
    resp = client.post(
        "/extract",
        files={"file": ("test.png", img_bytes, "image/png")}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "text" in data
    assert isinstance(data["text"], str)

def test_extract_bad_format(client):
    resp = client.post(
        "/extract",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert resp.status_code == 415
