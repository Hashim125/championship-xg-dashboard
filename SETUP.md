# Password Protection Setup Guide

This dashboard is password-protected. Follow these steps to set it up:

## Step 1: Generate Password Hash

Run the password hash generator:

```bash
python generate_password_hash.py
```

Enter your desired password when prompted. The script will output a hash like:
```
password_hash = "abc123def456..."
```

## Step 2: Update secrets.toml

Edit `.streamlit/secrets.toml` and replace the placeholder with your generated hash:

```toml
# Password for the dashboard
password_hash = "your_generated_hash_here"

# Snowflake credentials
[snowflake]
account = "TDAPVGQ-SL30706"
user = "HUMARJI"
warehouse = "COMPUTE_WH"
database = "CAFC_TEST_ANALYSIS"
schema = "PUBLIC"
private_key_path = "./keys/rsa_key_unencrypted.pem"
```

## Step 3: Deploy to Streamlit Community Cloud

1. Push your code to GitHub (secrets.toml is already in .gitignore)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. In the "Advanced settings", add your secrets:

```toml
password_hash = "your_generated_hash_here"

[snowflake]
account = "TDAPVGQ-SL30706"
user = "HUMARJI"
warehouse = "COMPUTE_WH"
database = "CAFC_TEST_ANALYSIS"
schema = "PUBLIC"
# Note: For Streamlit Cloud, you'll need to handle the private key differently
```

## Step 4: Add Private Key to Streamlit Cloud

For the Snowflake private key, you have two options:

### Option A: Paste key content directly
In `.streamlit/secrets.toml` on Streamlit Cloud:

```toml
[snowflake]
account = "TDAPVGQ-SL30706"
user = "HUMARJI"
warehouse = "COMPUTE_WH"
database = "CAFC_TEST_ANALYSIS"
schema = "PUBLIC"
private_key = """
-----BEGIN PRIVATE KEY-----
[paste your key content here]
-----END PRIVATE KEY-----
"""
```

Then update `database.py` to use the key content instead of file path.

### Option B: Use Streamlit secrets file
1. Upload your private key file to Streamlit Cloud secrets
2. Reference it in your code

## Security Notes

- **NEVER** commit `.streamlit/secrets.toml` or `keys/` directory to GitHub
- **NEVER** commit `.env` file
- Share the password securely with your team (use a password manager)
- The password hash cannot be reversed to get the original password
- Change the password by generating a new hash and updating secrets.toml

## Local Testing

Run locally:
```bash
streamlit run app.py
```

Enter your password when prompted.
