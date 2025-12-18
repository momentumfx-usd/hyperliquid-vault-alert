import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ================== CONFIG ==================
VAULT_ADDRESS = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
TO_EMAIL = "hs88008811@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "YOUR_GMAIL@gmail.com"
EMAIL_PASS = "YOUR_GMAIL_APP_PASSWORD"
# ============================================

URL = "https://api.hyperliquid.xyz/info"

def fetch_positions():
    payload = {
        "type": "vaultDetails",
        "vaultAddress": VAULT_ADDRESS
    }

    r = requests.post(URL, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()

    positions = data.get("positions", [])

    parsed = []
    for p in positions:
        size = float(p["position"]["szi"])
        entry = float(p["position"]["entryPx"])
        mark = float(p["position"]["markPx"])
        pnl = float(p["position"]["pnl"])
        margin = float(p["position"]["margin"])
        funding = float(p["position"]["funding"])
        liquidation = p["position"].get("liqPx", "NA")

        position_value = abs(size * mark)

        roi = (pnl / margin * 100) if margin != 0 else 0

        parsed.append({
            "coin": p["coin"],
            "size": size,
            "position_value": position_value,
            "entry": entry,
            "mark": mark,
            "pnl": pnl,
            "roi": roi,
            "liq": liquidation,
            "margin": margin,
            "funding": funding
        })

    parsed.sort(key=lambda x: x["position_value"], reverse=True)
    return parsed[:10]


def send_email(rows):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = "Hyperliquid Vault – Top 10 Positions"

    body = ""
    for i, r in enumerate(rows, 1):
        body += (
            f"{i}. {r['coin']}\n"
            f"   Size: {r['size']}\n"
            f"   Position Value: ${r['position_value']:.2f}\n"
            f"   Entry Price: {r['entry']}\n"
            f"   Mark Price: {r['mark']}\n"
            f"   PnL: {r['pnl']:.2f} ({r['roi']:.2f}%)\n"
            f"   Liquidation: {r['liq']}\n"
            f"   Margin: {r['margin']}\n"
            f"   Funding: {r['funding']}\n"
            "----------------------------------\n"
        )

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()


if __name__ == "__main__":
    top10 = fetch_positions()
    send_email(top10)
