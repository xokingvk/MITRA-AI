import urllib.request
import urllib.error
import json
import time
import os

def run_test():
    speech_path = os.path.join(os.path.dirname(__file__), "..", "sample_speech_maternity.wav")
    with open(speech_path, "rb") as f:
        audio_bytes = f.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="file"; filename="recording.wav"\r\n')
    body.extend(b"Content-Type: audio/wav\r\n\r\n")
    body.extend(audio_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="language"\r\n\r\n')
    body.extend(b"en-IN\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    url = "https://mitra-ai-6a4h.onrender.com/api/voice/transcribe"
    print(f"Sending POST to {url} (Audio size: {len(audio_bytes)} bytes)...")
    print(f"Spoken phrase in audio: 'I need maternal health insurance schemes'")

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
        method="POST"
    )

    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            elapsed = time.time() - start_t
            resp_data = resp.read().decode("utf-8")
            print(f"\n==========================================")
            print(f"HTTP STATUS: {resp.status} OK (elapsed: {elapsed:.2f}s)")
            print(f"Date: {resp.headers.get('Date')}")
            print(f"rndr-id: {resp.headers.get('rndr-id')}")
            print(f"CF-RAY: {resp.headers.get('CF-RAY')}")
            print(f"==========================================")
            print("\nRESPONSE BODY:")
            print(resp_data)
    except Exception as e:
        print(f"\nREQUEST EXCEPTION: {str(e)}")

if __name__ == "__main__":
    run_test()
