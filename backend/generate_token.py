#!/usr/bin/env python3
"""
Script to generate a new Google OAuth2 token using existing credentials.json
"""

import os
import sys
from app.services.auth_service import AuthService

def main():
    # Get the paths
    credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    token_path = os.path.join(os.path.dirname(__file__), "token.json")
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"❌ Error: credentials.json not found at {credentials_path}")
        print("Please make sure you have downloaded the credentials.json file from Google Cloud Console")
        sys.exit(1)
    
    print(f"✅ Found credentials.json at {credentials_path}")
    
    # Initialize auth service
    auth_service = AuthService(credentials_path=credentials_path, token_path=token_path)
    
    try:
        # Get authorization URL
        auth_url = auth_service.get_authorization_url()
        print("\n🔗 Authorization URL generated successfully!")
        print(f"\n📋 Please visit this URL in your browser:")
        print(f"{auth_url}")
        print(f"\n📝 After authorization, you'll be redirected to a URL like:")
        print(f"http://localhost:8000/api/auth/callback?code=YOUR_AUTH_CODE&state=...")
        print(f"\n🔑 Copy the 'code' parameter from that URL and run:")
        print(f"python -c \"from app.services.auth_service import AuthService; import os; auth = AuthService('{credentials_path}', '{token_path}'); auth.handle_callback('YOUR_AUTH_CODE')\"")
        
    except Exception as e:
        print(f"❌ Error generating authorization URL: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 