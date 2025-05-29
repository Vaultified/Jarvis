from gmail_service import send_email
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())

def main():
    # Test email details
    to = ["sujinsr2457@gmail.com"]  # Your email address
    subject = "Test Email from Gmail Service"
    body = "This is a test email sent using the Gmail API."
    
    print("\n=== Starting Test ===")
    print("Sending test email...")
    result = send_email(to=to, subject=subject, body=body)
    
    if result["success"]:
        print("\nEmail sent successfully!")
        print(f"Message ID: {result['details']['messageId']}")
    else:
        print("\nFailed to send email:")
        print(result["message"])
        if "error" in result["details"]:
            print(f"Error details: {result['details']['error']}")

if __name__ == "__main__":
    main() 