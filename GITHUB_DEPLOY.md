# GitHub Deployment Guide

## Quick Steps to Deploy

### 1. Initialize Git Repository (if not already done)

```bash
cd "/Users/hashim.umarji/Desktop/My Work/stats-overview"
git init
git add .
git commit -m "Initial commit: Championship xG Dashboard with password protection"
```

### 2. Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it (e.g., `championship-xg-dashboard`)
4. Make it **Private** (recommended for work data)
5. **Do NOT** initialize with README (you already have files)
6. Click "Create repository"

### 3. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/championship-xg-dashboard.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `championship-xg-dashboard`
5. Main file path: `app.py`
6. Click "Advanced settings"
7. Paste your secrets (copy from `.streamlit/secrets.toml`):

```toml
password_hash = "b84f8122b49231c06a212ada6ffce6db0a0fa611105e637c12155e826685c65e"

[snowflake]
account = "TDAPVGQ-SL30706"
user = "HUMARJI"
warehouse = "COMPUTE_WH"
database = "CAFC_TEST_ANALYSIS"
schema = "PUBLIC"
private_key_path = "./keys/rsa_key_unencrypted.pem"
```

8. Click "Deploy"

### 5. Handle Private Key for Deployment

**Important:** You'll need to modify `database.py` for cloud deployment since you can't upload files directly.

Update `.streamlit/secrets.toml` on Streamlit Cloud to include the private key content:

```toml
password_hash = "your_hash_here"

[snowflake]
account = "TDAPVGQ-SL30706"
user = "HUMARJI"
warehouse = "COMPUTE_WH"
database = "CAFC_TEST_ANALYSIS"
schema = "PUBLIC"
private_key = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
[paste your full private key here]
...
-----END PRIVATE KEY-----
"""
```

Then update `database.py` to check for both file path and direct key content.

### 6. Share with Your Team

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this URL and the password (`CharltonXG2025` or your custom password) with your colleagues.

## Security Checklist

✅ `.gitignore` includes `.streamlit/secrets.toml`
✅ `.gitignore` includes `keys/` directory
✅ `.gitignore` includes `.env` file
✅ Repository is set to **Private** on GitHub
✅ Password is strong and shared securely
✅ Private key is never committed to git

## Updating the Password

To change the password:

1. Run `python generate_password_hash.py`
2. Enter your new password
3. Copy the generated hash
4. Update `.streamlit/secrets.toml` locally
5. Update secrets on Streamlit Cloud dashboard settings
6. Share new password with your team

## Troubleshooting

**Error: "No module named 'snowflake'"**
- Make sure `requirements.txt` is in your repo
- Streamlit Cloud will auto-install dependencies

**Error: "Private key not found"**
- You need to embed the private key content in secrets.toml
- See step 5 above

**Password not working**
- Make sure you copied the full password hash
- Check for extra spaces or line breaks
- Regenerate the hash if needed
