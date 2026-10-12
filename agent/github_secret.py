"""Saves the new TikTok refresh token back into the GitHub repo secret,
so the agent keeps working for months without you touching anything."""
import base64
import os

import requests


def update_secret(name, value):
    pat = os.environ.get("GH_PAT")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not pat or not repo:
        print(f"[secret] GH_PAT or GITHUB_REPOSITORY missing, {name} not updated")
        return False
    from nacl import encoding, public

    h = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
    key = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
                       headers=h, timeout=30).json()
    box = public.SealedBox(public.PublicKey(key["key"].encode(), encoding.Base64Encoder()))
    enc = base64.b64encode(box.encrypt(value.encode())).decode()
    r = requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/{name}",
                     headers=h, json={"encrypted_value": enc, "key_id": key["key_id"]},
                     timeout=30)
    ok = r.status_code in (201, 204)
    print(f"[secret] {name} updated" if ok else f"[secret] update failed {r.status_code}")
    return ok
