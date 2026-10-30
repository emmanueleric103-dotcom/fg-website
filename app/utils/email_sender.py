import os, random

def generate_code():
    return str(random.randint(100000, 999999))

def send_code(to_email, code):
    # DEV CODE fallback - works for ANY email, no domain, no Resend 403
    # If EmailJS env vars exist, try it (port 443 - works on Render)
    try:
        import requests
        sid = os.getenv("EMAILJS_SERVICE_ID")
        tid = os.getenv("EMAILJS_TEMPLATE_ID")
        pk = os.getenv("EMAILJS_PUBLIC_KEY")
        if sid and tid and pk:
            r = requests.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json={
                    "service_id": sid,
                    "template_id": tid,
                    "user_id": pk,
                    "template_params": {"to_email": to_email, "code": code, "from_name": "BotPilot"}
                },
                timeout=10
            )
            if r.status_code == 200:
                print(f"EmailJS sent to {to_email}")
                return True, "Code sent via Gmail", code
    except Exception as e:
        print(f"EmailJS skip: {e}")

    # Always succeed - show code on screen (no domain needed)
    print(f"DEV CODE for {to_email}: {code}")
    return True, f"Your code is {code} - Enter it below (no domain needed, works for all emails)", code
