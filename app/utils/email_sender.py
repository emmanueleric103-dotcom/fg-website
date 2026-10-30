import os, random, requests

def generate_code():
    return str(random.randint(100000, 999999))

def send_code(to_email, code):
    # Try EmailJS with Gmail App Password (port 443 - works on Render)
    try:
        service_id = os.getenv("EMAILJS_SERVICE_ID")
        template_id = os.getenv("EMAILJS_TEMPLATE_ID")
        public_key = os.getenv("EMAILJS_PUBLIC_KEY")
        if service_id and template_id and public_key:
            r = requests.post("https://api.emailjs.com/api/v1.0/email/send",
                json={
                    "service_id": service_id,
                    "template_id": template_id,
                    "user_id": public_key,
                    "template_params": {
                        "to_email": to_email,
                        "to_name": to_email.split('@')[0],
                        "code": code,
                        "from_name": "BotPilot"
                    }
                }, timeout=15)
            if r.status_code == 200:
                return True, "Code sent via Gmail", code
    except Exception as e:
        print(f"EmailJS failed: {e}")

    # Fallback - shows code on screen, works for ANY email, no domain
    print(f"DEV CODE for {to_email}: {code}")
    return True, f"Your code is {code} - Enter it below (no domain needed)", code
