import urllib.request
import urllib.error
import json
import time
import os

def test_microphone_webm_upload():
    webm_path = os.path.join(os.path.dirname(__file__), "..", "sample_microphone_speech.webm")
    if not os.path.exists(webm_path):
        print(f"File not found: {webm_path}")
        return

    with open(webm_path, "rb") as f:
        audio_bytes = f.read()

    boundary = "----WebKitFormBoundaryMicrophoneWebMTest"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="file"; filename="microphone_recording.webm"\r\n')
    body.extend(b"Content-Type: audio/webm\r\n\r\n")
    body.extend(audio_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="language"\r\n\r\n')
    body.extend(b"en-IN\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    url = "https://mitra-ai-6a4h.onrender.com/api/voice/transcribe"
    print(f"\n=======================================================")
    print(f"TESTING REAL BROWSER MICROPHONE AUDIO/WEBM UPLOAD")
    print(f"Target: {url}")
    print(f"MIME type: audio/webm")
    print(f"File size: {len(audio_bytes)} bytes")
    print(f"Spoken phrase: 'I am pregnant and I need government health schemes'")
    print(f"=======================================================")

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        method="POST"
    )

    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            elapsed = time.time() - start_t
            resp_data = resp.read().decode("utf-8")
            print(f"HTTP STATUS: {resp.status} OK (elapsed: {elapsed:.2f}s)")
            print(f"Date: {resp.headers.get('Date')}")
            print(f"rndr-id: {resp.headers.get('rndr-id')}")
            print(f"CF-RAY: {resp.headers.get('CF-RAY')}")
            print("\nRESPONSE BODY:")
            print(resp_data)
            try:
                parsed = json.loads(resp_data)
                print("\nTRANSCRIPTION RESULT:")
                print(f"  transcript: '{parsed.get('transcript')}'")
                print(f"  provider: '{parsed.get('provider')}'")
            except Exception:
                pass
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_t
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP ERROR: {e.code} {e.reason} (elapsed: {elapsed:.2f}s)")
        print("ERROR BODY:\n" + err_body)
    except Exception as e:
        print(f"REQUEST FAILED: {str(e)}")

if __name__ == "__main__":
    test_microphone_webm_upload()
