import hashlib
import getpass

# Get password from user
password = getpass.getpass("Enter the password you want to use: ")

# Generate SHA256 hash
password_hash = hashlib.sha256(password.encode()).hexdigest()

print("\n" + "="*60)
print("Password hash generated successfully!")
print("="*60)
print(f"\nAdd this line to .streamlit/secrets.toml:")
print(f'\npassword_hash = "{password_hash}"')
print("\n" + "="*60)
