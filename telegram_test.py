#!/usr/bin/env python3
"""Test polaczenia z botem Telegram: wysyla wiadomosc do wszystkich odbiorcow.

Sekrety (tylko jako GitHub Actions secrets, nigdy w repo ani w logach):
  TG_TOKEN     - token bota od @BotFather
  TG_CHAT_IDS  - numery czatow odbiorcow po przecinku (ty + znajomi)
Opcjonalnie:
  TG_TEXT      - tresc wiadomosci testowej

Skrypt nie drukuje tokenu ani numerow czatow (logi publicznego repo sa publiczne);
pokazuje tylko, ilu odbiorcom wiadomosc dotarla i opis bledu od Telegrama.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def send_message(token: str, chat_id: str, text: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
            body = json.loads(r.read().decode())
            return bool(body.get("ok")), ""
    except urllib.error.HTTPError as e:
        try:
            desc = json.loads(e.read().decode()).get("description", "")
        except Exception:
            desc = ""
        return False, f"HTTP {e.code}: {desc}"
    except Exception as e:  # siec, timeout
        return False, type(e).__name__


def main() -> int:
    token = os.environ.get("TG_TOKEN", "").strip()
    chats = [c.strip() for c in os.environ.get("TG_CHAT_IDS", "").split(",") if c.strip()]
    text = os.environ.get("TG_TEXT", "").strip() or "MeteoPanel: test powiadomien. Jesli to widzisz, bot dziala."

    if not token:
        print("Brak sekretu TG_TOKEN (Settings -> Secrets and variables -> Actions).")
        return 1
    if not chats:
        print("Brak sekretu TG_CHAT_IDS (numery czatow po przecinku).")
        return 1

    ok_count = 0
    for i, chat in enumerate(chats, 1):
        ok, err = send_message(token, chat, text)
        if ok:
            ok_count += 1
            print(f"Odbiorca {i}/{len(chats)}: wyslano")
        else:
            print(f"Odbiorca {i}/{len(chats)}: BLAD {err}")

    print(f"Dotarlo do {ok_count} z {len(chats)} odbiorcow.")
    return 0 if ok_count == len(chats) else 1


if __name__ == "__main__":
    sys.exit(main())
