import os
import requests
import smtplib
from email.mime.text import MIMEText

# ================= CONFIG =================
VAULT_ADDRESS = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
TO_EMAIL = "atrade2501@gmail.com"

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# =========================================


def fetch_positions():
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "vaultDetails",
        "vaultAddress": VAULT_ADDRESS
    }

    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()

    positions = data.get("positions", [])

    results = []

    for p in positions:
        pos = p.get("position", {})

        try:
            size = float(pos.get("szi", 0))
            entry = float(pos.get("entryPx", 0))
            mark = float(pos.get("markPx", 0))
            pnl = float(pos.get("pnl", 0))
            margin = float(pos.get("margin", 0))
            funding = float(pos.get("funding", 0))
            liq = pos.get("liqPx", "NA")

            position_value = abs(size * mark)
            roi = (pnl / margin * 100) if margin != 0 else 0

            results.append({
                "coin": p.get("coin", "NA"),
                "size": size,
                "position_value": position_value,
                "entry": entry,
                "mark": mark,
                "pnl": pnl,
                "roi": roi,
                "liq": liq,
                "margin": margin,
                "funding": funding
            })
        except Exception:
            continue

    results.sort(key=lambda x: x["position_value"], reverse=True)
    return results[:10]


def send_email(rows):
    if not rows:
        body = "No open positions found in the vault at this time."
    else:
        body = ""
        for i, r in enumerate(rows, 1):
            body += (
                f"{i}. {r['coin']}\n"
                f"   Size: {r['size']}\n"
                f"   Position Value: ${r['position_value']:.2f}\n"
                f"   Entry Price: {r['entry']}\n"
                f"   Mark Price: {r['mark']}\n"
                f"   PnL: {r['pnl']:.2f} ({r['roi']:.2f}%)\n"
                f"   Liquidation Price: {r['liq']}\n"
                f"   Margin: {r['margin']}\n"
                f"   Funding: {r['funding']}\n"
                "----------------------------------\n"
            )

    msg = MIMEText(body, "plain")
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = "Hyperliquid Vault – Top 10 Positions"

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)


if __name__ == "__main__":
    positions = fetch_positions()
    send_email(positions)
