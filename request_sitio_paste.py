import requests

res = requests.post("https://dpaste.org/api/", data={
    "content": key.decode(),
    "syntax": "text",
    "expiry_days": 1
})
print("[🌐] Clave subida a:", res.text)
