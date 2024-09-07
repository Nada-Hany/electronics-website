import smtplib

HOST = "smtp.gmail.com"
PORT = 587

FROM_EMAIL = ""
TO_EMAIL = ""
PASSWORD = ""

MESSAGE = """Subject: <add mail subject here>
<add mail content here>"""

smtp = smtplib.SMTP(HOST, PORT)

status_code, response = smtp.ehlo()
status_code, response = smtp.starttls()
status_code, response = smtp.login(FROM_EMAIL, PASSWORD)

smtp.sendmail(FROM_EMAIL, TO_EMAIL, MESSAGE)
print("email got sent")
smtp.quit()