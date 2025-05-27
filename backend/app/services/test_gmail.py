from gmail_service import send_email
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())

# Test sending an email
print("\nAttempting to send test email...")
result = send_email(
    to=["sujinsr2457@gmail.com"],
    subject="Test Email",
    body="This is a test email.",
    mime_type="text/plain"
)

print("\nFinal Result:", result) 