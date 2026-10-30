import os
import requests
import logging

def send_verification_email(to_email, code, login=False):
    """
    Send via Resend HTTP API on port 443 - bypasses Render SMTP block on 25/587/465
    Returns (sent:bool, debug_info:str)
    """
    api_key = os.getenv('RESEND_API_KEY', '').strip()
    from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev').strip()
    from_name = os.getenv('FROM_NAME', 'BotPilot').strip()
    
    subject = "Your BotPilot Login Code" if login else "Your BotPilot Verification Code"
    html = f"""
    <div style="font-family:Inter,Arial,sans-serif; max-width:520px; margin:auto; background:#0f0f12; color:#fff; border-radius:16px; overflow:hidden;">
      <div style="padding:28px; background:linear-gradient(135deg,#7c3aed,#06b6d4);">
        <h1 style="margin:0; font-size:24px;">{from_name}</h1>
        <p style="margin:8px 0 0; opacity:0.9;">Perfect Sensitivity Lab</p>
      </div>
      <div style="padding:28px;">
        <h2 style="margin:0 0 12px;">Your code is: <span style="letter-spacing:4px; color:#a78bfa;">{code}</span></h2>
        <p style="color:#aaa; line-height:1.6;">Use this 6-digit code to {"login to" if login else "verify"} your BotPilot account. It expires in 10 minutes.</p>
        <div style="margin:24px 0; padding:16px; background:#1a1a1f; border-radius:12px; border:1px solid #2a2a33; text-align:center;">
          <span style="font-size:32px; letter-spacing:8px; font-weight:800;">{code}</span>
        </div>
        <p style="color:#666; font-size:12px;">If you didn't request this, ignore this email.</p>
      </div>
    </div>
    """
    
    # No key -> debug mode (still works, shows code in logs/popup)
    if not api_key:
        msg = f"RESEND_API_KEY not set. DEV CODE for {to_email}: {code}"
        print(f"\n=== EMAIL DEBUG ===\n{msg}\n===================\n")
        logging.warning(msg)
        return False, f"DEV MODE: Your code is {code} (set RESEND_API_KEY in Render to send real Gmail)"
    
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": f"{from_name} <{from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html
            },
            timeout=15
        )
        if resp.status_code in (200, 201):
            print(f"Resend OK to {to_email}: {resp.json()}")
            return True, f"Code sent to {to_email} via Resend"
        else:
            err = resp.text[:500]
            print(f"Resend FAILED {resp.status_code}: {err}")
            return False, f"Resend error {resp.status_code}: {err} - DEV CODE: {code}"
    except Exception as e:
        print(f"Resend exception: {e}")
        return False, f"Email service error - DEV CODE: {code} ({e})"
