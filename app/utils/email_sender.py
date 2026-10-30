import os
import random

def generate_code():
    return str(random.randint(100000, 999999))

def send_code(to_email, code):
    print(f"DEV CODE for {to_email}: {code}")
    return True, f"Your code is {code} - Enter it below (no domain needed, works for all emails)", code

def send_verification_email(to_email, code):
    # auth.py calls this name - just call send_code
    return send_code(to_email, code)
