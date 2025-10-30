# Deployment Guide for Championship xG Dashboard

This guide explains how to make your Streamlit dashboard available to your colleagues privately and securely.

## Table of Contents
1. [Option 1: Streamlit Community Cloud (Easiest, Free)](#option-1-streamlit-community-cloud)
2. [Option 2: Hetzner Cloud (Most Control, ~€5/month)](#option-2-hetzner-cloud)
3. [Option 3: Internal Network (Free, Local Only)](#option-3-internal-network)

---

## Option 1: Streamlit Community Cloud (Easiest, Free)

**Best for:** Quick deployment, no technical setup, free hosting

**Limitations:**
- Dashboard becomes public by default (can set password protection)
- Your Snowflake credentials need to be stored in Streamlit Secrets
- Limited to 1GB RAM (should be fine for your app)

### Steps:

1. **Create a GitHub Repository:**
   ```bash
   cd "/Users/hashim.umarji/Desktop/My Work/stats-overview"
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub (Private Repo):**
   - Go to [github.com](https://github.com) and create a **private** repository
   - Follow GitHub's instructions to push your code

3. **Deploy on Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your private repository
   - Add Snowflake credentials to "Secrets" section

4. **Add Password Protection:**
   Create `.streamlit/secrets.toml`:
   ```toml
   [passwords]
   admin_user = "your_password_here"
   ```

   Update `app.py` to add authentication at the top.

**Pros:** Free, easy, automatic updates
**Cons:** Public infrastructure, limited resources

---

## Option 2: Hetzner Cloud (Recommended for Work)

**Best for:** Professional deployment, full control, private hosting

**Cost:** €4-10/month depending on server size

### What is Hetzner?

Hetzner is a **German cloud hosting provider** - think of it as a cheaper alternative to AWS/Azure/Google Cloud. You rent a virtual server (VPS) and can run whatever you want on it.

**Why Hetzner?**
- ✅ Much cheaper than AWS/Azure (~€5/month vs $20-50)
- ✅ Excellent performance
- ✅ GDPR compliant (EU-based)
- ✅ Simple to use
- ✅ Full control over your server

### Deployment Steps:

#### 1. Create Hetzner Account
- Go to [hetzner.com/cloud](https://www.hetzner.com/cloud)
- Sign up for an account
- Add payment method

#### 2. Create a Server (Cloud VPS)
- Click "Add Server"
- **Location:** Choose closest to you (e.g., UK for better speed)
- **Image:** Ubuntu 22.04
- **Type:** CX11 (2GB RAM, €4.15/month) - sufficient for your dashboard
- **Networking:** Enable IPv4
- **SSH Key:** Add your SSH key (or use password)
- Click "Create & Buy"

#### 3. Connect to Your Server
```bash
ssh root@YOUR_SERVER_IP
```

#### 4. Install Required Software
```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3-pip python3-venv nginx -y

# Create app directory
mkdir -p /opt/xg-dashboard
cd /opt/xg-dashboard
```

#### 5. Upload Your Dashboard
```bash
# From your local machine:
scp -r "/Users/hashim.umarji/Desktop/My Work/stats-overview"/* root@YOUR_SERVER_IP:/opt/xg-dashboard/
```

#### 6. Set Up Python Environment
```bash
# On server:
cd /opt/xg-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 7. Create Systemd Service (Auto-start on boot)
Create `/etc/systemd/system/xg-dashboard.service`:
```ini
[Unit]
Description=Championship xG Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/xg-dashboard
Environment="PATH=/opt/xg-dashboard/venv/bin"
ExecStart=/opt/xg-dashboard/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable xg-dashboard
systemctl start xg-dashboard
systemctl status xg-dashboard
```

#### 8. Set Up Nginx Reverse Proxy (for HTTPS)
Create `/etc/nginx/sites-available/xg-dashboard`:
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;  # Or your domain name

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/xg-dashboard /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 9. Add HTTPS (Optional but Recommended)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

#### 10. Set Up Firewall
```bash
ufw allow 22      # SSH
ufw allow 80      # HTTP
ufw allow 443     # HTTPS
ufw enable
```

### Access Control Options

**Option A: IP Whitelist**
Only allow specific IP addresses (your office network):
```nginx
# In nginx config, add:
location / {
    allow 123.456.789.0/24;  # Your office IP range
    deny all;

    proxy_pass http://localhost:8501;
    # ... rest of config
}
```

**Option B: HTTP Basic Auth**
Add username/password protection:
```bash
apt install apache2-utils -y
htpasswd -c /etc/nginx/.htpasswd teamuser
```

Update nginx config:
```nginx
location / {
    auth_basic "XG Dashboard";
    auth_basic_user_file /etc/nginx/.htpasswd;

    proxy_pass http://localhost:8501;
    # ... rest of config
}
```

**Option C: VPN (Most Secure)**
Set up Tailscale/WireGuard so only people on your company VPN can access.

---

## Option 3: Internal Network (Free, Local Only)

**Best for:** If all colleagues are in the same office network

### Steps:

1. **Run on Your Machine:**
   ```bash
   streamlit run app.py --server.port 8501
   ```

2. **Find Your IP Address:**
   ```bash
   ipconfig getifaddr en0  # On Mac
   ```

3. **Share URL with Colleagues:**
   - Give them: `http://YOUR_LOCAL_IP:8501`
   - They must be on the same network

4. **Keep Running 24/7:**
   - Keep your laptop running and connected
   - Use `caffeinate` command to prevent sleep:
   ```bash
   caffeinate -s streamlit run app.py
   ```

**Pros:** Free, simple, no cloud setup
**Cons:** Only works on local network, requires your machine to be always on

---

## Recommendation for Your Team

**Best Option: Hetzner Cloud with Basic Auth**

1. Cost: ~€5/month
2. Professional and reliable
3. Accessible from anywhere
4. Password protected
5. Easy to maintain

**Second Best: Streamlit Community Cloud**
- Free but public infrastructure
- Good for testing/proof of concept

---

## Security Best Practices

1. **Never commit `.env` or `keys/` to Git**
   - Already in `.gitignore`
   - Store credentials securely on server

2. **Use HTTPS** (Hetzner setup includes this)

3. **Regular Updates:**
   ```bash
   git pull origin main
   systemctl restart xg-dashboard
   ```

4. **Monitor Access:**
   ```bash
   tail -f /var/log/nginx/access.log
   ```

---

## Cost Comparison

| Option | Monthly Cost | Setup Time | Maintenance |
|--------|--------------|------------|-------------|
| Streamlit Cloud | Free | 15 min | Low |
| Hetzner | €4-10 | 1-2 hours | Medium |
| Local Network | Free | 5 min | High |

---

## Need Help?

- Hetzner Docs: [docs.hetzner.com](https://docs.hetzner.com)
- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io)
- Contact me for deployment support

---

## Quick Start Command Summary

### Hetzner:
```bash
# On server:
cd /opt/xg-dashboard
git pull  # Update code
systemctl restart xg-dashboard  # Restart app
```

### Local:
```bash
cd "/Users/hashim.umarji/Desktop/My Work/stats-overview"
streamlit run app.py
```
