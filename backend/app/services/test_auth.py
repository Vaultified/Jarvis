from auth_service import AuthService

def main():
    # wate an instance of AuthService
    auth = AuthService()
    
    # Get the authorization URL
    auth_url = auth.get_auth_url()
    print("\nPlease visit this URL to authorize the application:")
    print(auth_url)
    
    # Wait for the authorization code
    code = input("\nEnter the authorization code from the callback URL: ")
    
    # Exchange the code for tokens
    tokens = auth.handle_callback(code)
    print("\nAuthentication successful! Here are your tokens:")
    print(f"Access Token: {tokens['access_token']}")
    print(f"Refresh Token: {tokens['refresh_token']}")
    print(f"Scopes: {tokens['scopes']}")
    
    # Verify we can get Gmail service
    try:
        gmail = auth.get_gmail_service()
        profile = gmail.users().getProfile(userId='me').execute()
        print(f"\nSuccessfully connected to Gmail as: {profile.get('emailAddress')}")
    except Exception as e:
        print(f"\nError connecting to Gmail: {str(e)}")

if __name__ == "__main__":
    main() 