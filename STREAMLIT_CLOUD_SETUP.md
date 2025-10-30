# Streamlit Cloud Deployment - Quick Setup Guide

## Changes Made for Cloud Deployment

✅ Updated `database.py` to support both local and cloud deployment
✅ App now reads from Streamlit secrets when deployed to cloud
✅ Local development still works with `.env` file

## Deployment Steps

### 1. Create GitHub Repository

```bash
cd "/Users/hashim.umarji/Desktop/My Work/stats-overview"
git init
git add .
git commit -m "Initial commit: Championship xG Dashboard"
```

Then create a **private** repository on GitHub and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/championship-xg-dashboard.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `championship-xg-dashboard`
5. Main file path: `app.py`
6. Click "Advanced settings"

### 3. Add Secrets

In the "Secrets" section, paste the following (replacing with your actual values):

```toml
password_hash = "b84f8122b49231c06a212ada6ffce6db0a0fa611105e637c12155e826685c65e"

[snowflake]
account = "TDAPVGQ-SL30706"
user = "HUMARJI"
warehouse = "COMPUTE_WH"
database = "CAFC_TEST_ANALYSIS"
schema = "PUBLIC"
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAzTiTEol8HJfRDUwzIX7czJ+nSf+5/uZoMp3BZfJBMT7hJAX0
zKdoETVjljQe/pNByQLPG0RqTPyCsDScrM8c90L50DoqFHQRdjLwWxeGfFEXe9zE
3znxZdvQzNOfKCvwwnxiRRzG0UeF8TdvHRZIBbz+1onHwRdj2/SMgV4U7lwEGpro
mFrnEVRQdijZ5tQH+k97yt5KORxTfBN0uQxEPI1KvsbdWFEv6LMsYAOLljKdO5bM
bKbSUzxfX3Jo9MyQv8c7sd4MkVZtp7glWEeVQ8yOKl/6qTfB4yswjYIRl+7Ia0aN
SuKJGXPNIdM0qqCLcNrhHsx9ERGIIuBZoPMgtwIDAQABAoIBADfZ6czlte1iM/bW
giPfjt/xo2m0Oz5wHnOIE5ZXM/7fCg7vwAvik6P7T7sVPEo0cXbvWMYm/HcvUbH6
35j4VP3GMI7HBaTDYe01N8zSvjsfJrEDCGFoN5ZtGIpmHa6lJsUHbQc6KbHTMVTQ
rWDRK5DEOubQYJjgcMDv8T1UCYZE72curQdt0FhiJsfblvOsZ+45foKqEGCqWXCu
OM9RvhUT0p/85gWLcnr+eGJBsw6lXqFurDDRp/9ODpqMyrelq7sEwHGapD0VHwxw
lrKohsHoEfu+oKuKVfmP1Wupcx5andoNv4SgJleUqVn0rZ9GQntgXtnRenQ09H+J
v9QLVGECgYEA+pVDpXHbIs/ivItfCSzq+9URGtirAJNqejGBRM4wUUEJ+raHkdL7
lGEop4dUosR0GM0AyXxTTaVqF+Fix5X6trX0MbL4PKf67CyK6ApDhhTCCQOK+O41
jVDvGGZUgIohqOlzIESED9LzAe/m0iINxvTefTSlNT6SzTMLwJ7EHnUCgYEA0ahG
YVGh0K64YPbA4Euhk0FpmW/soJZTmwNikj30gFkCfAMzqz+64cRE8c3NbwsmaieM
dTImuagM+/ypw2jNyM4NNIEQU/aK7RswaNV2Oz3BYPwb2OEk+asCwR+sWYoSwsb0
pRUSPtV5JQHXJgWeSDioeruz0jfkoFkXfeJjtPsCgYEAqDKEw4qXAtjzYodSdUA3
Qm6UGqcQsURCFl8gW+TivcegQS8/9Hvf7osA1OKbxt2C6BrCynuvFtFPU1QwD7P2
I6oijTGKOnyuitSjMHmjNV69l3tPTyPlwkNvGbumQNl3GoAIjMIwusZn4wb6slW1
VbSLmxM5SXIE68O1wcdP8PkCgYEAloAKTa/wzcGuf4SCPkBscy2gpVFv9nMS/xK1
/q7UxhGfM/CEdajg+VIP/9gxYUYKxGcxb6uZmupkr7rXDnw8RKqNViRT2UIAxmYf
IRIitjIFkB5Jyy0LguHcr0+SRBBWmVWCpsJyf4J0XTlt/VBJKCTr5Ha7heszhluN
/oK1+mMCgYEAyPJBwjikikagHPVqFbEWACXA1Vde8thOEcNYpJaZovqglbDG/I9c
g9c6kSbjWpi7cLHc2eAagoG1/WS5v+Bb4OhNI05e0HjAEgzflU8v+rDL+Ud9YR48
4rnNsO4vc95Q3K91JbWP+Pv63YPRf0vIL+sIjWnnoAKjD+SfhJcTSus=
-----END RSA PRIVATE KEY-----"""
```

### 4. Deploy

Click "Deploy" and wait for your app to build!

### 5. Share with Your Team

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this URL and the password (`CharltonXG2025`) with your colleagues.

## Important Notes

- ✅ Your app works both locally (with `.env`) and on Streamlit Cloud (with secrets)
- ✅ `.gitignore` prevents sensitive files from being committed
- ✅ GitHub repo should be **private** for security
- ✅ Password protects your dashboard from unauthorized access

## Updating Your App

To update after making changes:

```bash
git add .
git commit -m "Update dashboard"
git push
```

Streamlit Cloud will automatically redeploy!

## Changing the Password

1. Run: `python generate_password_hash.py`
2. Enter your new password
3. Copy the generated hash
4. Update secrets on Streamlit Cloud (Settings → Secrets)
5. Share new password with your team

## Security Checklist

✅ Repository is **private** on GitHub
✅ Secrets are stored in Streamlit Cloud, not in code
✅ `.env` and `keys/` are in `.gitignore`
✅ Password protection is enabled

## Need Help?

- Streamlit Cloud Docs: [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- GitHub Issues: Create an issue in your repository

---

## About Hetzner (for Multiple Projects)

**Yes, you can host multiple projects on one Hetzner server!**

If you have multiple Streamlit apps to deploy:

### Option A: Multiple Apps on Streamlit Cloud
- Deploy each project separately (free)
- Each gets its own URL
- Limitations: 1GB RAM per app, public infrastructure

### Option B: One Hetzner Server for All Apps
- Rent one VPS (~€5-10/month)
- Run multiple Streamlit apps on different ports:
  - App 1: `streamlit run app1.py --server.port 8501`
  - App 2: `streamlit run app2.py --server.port 8502`
  - App 3: `streamlit run app3.py --server.port 8503`
- Use Nginx to route different domains/paths to different apps
- Full control, private hosting, cost-effective for multiple apps

**Recommendation:**
- Start with Streamlit Cloud for this project (free, easy)
- If you have 3+ projects, consider Hetzner (more cost-effective)
