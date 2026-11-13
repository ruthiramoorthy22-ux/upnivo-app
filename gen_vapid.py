"""Run once:  python gen_vapid.py   -> paste the 2 lines into your .env (push notifications)."""
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization as S
b = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode()
k = ec.generate_private_key(ec.SECP256R1())
print("VAPID_PRIVATE_KEY=" + b(k.private_numbers().private_value.to_bytes(32, "big")))
print("VAPID_PUBLIC_KEY=" + b(k.public_key().public_bytes(S.Encoding.X962, S.PublicFormat.UncompressedPoint)))
