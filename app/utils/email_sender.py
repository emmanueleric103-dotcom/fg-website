import os
import random

def generate_code():
    return str(random.randint(100000, 999999))

def send_code(to_email, code):
    print(f"DEV CODE for {to_email}: {code}")
    return True, f"Your code is {code} - Enter it below (no domain needed, works for all emails)", code
