# BotPilot Perfect Zip - FF + COD + Login with Resend API + iPhone fix

## What is fixed
- **FF + COD tabs** in one page `/tools/sensitivity` - no 404
- **iPhone model selector** (7 to 15 Pro Max) instead of RAM - uses real hz + DPI factor
- **Resend HTTP API (port 443)** - Gmail codes work on Render free tier (SMTP 25/587 is blocked)
- **iPhone input fix**: font-size 16px (no auto zoom), 100dvh, safe-area-inset, touch-action:manipulation, -webkit-overflow-scrolling
- **Auto-create tables** - fixes 500 error on first deploy

## Setup on Render
1. Add env vars in Dashboard > Environment:
```
RESEND_API_KEY=re_your_key_from_resend.com
FROM_EMAIL=onboarding@resend.dev
FROM_NAME=BotPilot
SECRET_KEY=any-random-string
```

2. Get Resend key free:
- resend.com > Sign up > API Keys > Create > Sending access > copy re_...

Free tier 100 emails/day, no domain verification needed if using onboarding@resend.dev

3. Deploy logs should show:
```
AUTO-SEED OK - All tables created including User, SensitivityReview
```

## Local run
```
pip install -r requirements.txt
python run.py
```

## Routes
- / -> Home
- /tools/sensitivity -> FF + COD Lab (perfect)
- /auth/register -> Gmail code register
- /auth/login -> Password or Gmail code login
- /auth/verify?email=xxx -> Enter code
