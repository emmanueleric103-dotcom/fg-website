import os, random, requests
def generate_code():
    return str(random.randint(100000, 999999))
def send_code(to_email, code):
    try:
        sid=os.getenv("EMAILJS_SERVICE_ID")
        tid=os.getenv("EMAILJS_TEMPLATE_ID")
        pk=os.getenv("EMAILJS_PUBLIC_KEY")
        if sid and tid and pk:
            r=requests.post("https://api.emailjs.com/api/v1.0/email/send", json={"service_id":sid,"template_id":tid,"user_id":pk,"template_params":{"to_email":to_email,"code":code}}, timeout=15)
            if r.status_code==200:
                return True,"Code sent via Gmail",code
    except Exception as e:
        print(e)
    print(f"DEV CODE for {to_email}: {code}")
    return True,f"Your code is {code} - Enter it below",code
