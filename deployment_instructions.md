# Deployment Instructions for clinical-rnaseq.com

## Server Setup

### 1. Install Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
```

### 2. Set Up Project Directory

```bash
# Create project directory
sudo mkdir -p /var/www/clinical-rnaseq.com
sudo chown $USER:$USER /var/www/clinical-rnaseq.com

# Clone repository (or upload your files)
git clone [your-repository-url] /var/www/clinical-rnaseq.com
cd /var/www/clinical-rnaseq.com
```

### 3. Set Up Python Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Build Vue.js Frontend

```bash
cd prime_vue
npm install
npm run build
cd ..
```

### 5. Configure Nginx

```bash
# Copy Nginx configuration
sudo cp nginx_config.conf /etc/nginx/sites-available/clinical-rnaseq.com

# Enable the site
sudo ln -s /etc/nginx/sites-available/clinical-rnaseq.com /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If the test passes, restart Nginx
sudo systemctl restart nginx
```

### 6. Set Up SSL Certificate

```bash
sudo certbot --nginx -d clinical-rnaseq.com -d www.clinical-rnaseq.com
```

### 7. Create Log Directory

```bash
sudo mkdir -p /var/log/clinical-rnaseq
sudo chown www-data:www-data /var/log/clinical-rnaseq
```

### 8. Set Up Systemd Service

```bash
# Copy service file
sudo cp systemd_service.service /etc/systemd/system/clinical-rnaseq.service

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable clinical-rnaseq.service
sudo systemctl start clinical-rnaseq.service
```

### 9. Set Permissions

```bash
# Set correct ownership for the project files
sudo chown -R www-data:www-data /var/www/clinical-rnaseq.com
```

### 10. Verify Deployment

```bash
# Check service status
sudo systemctl status clinical-rnaseq.service

# Check Nginx status
sudo systemctl status nginx

# Check logs if there are issues
sudo journalctl -u clinical-rnaseq.service
```

## Maintenance

### Updating the Application

```bash
# Pull the latest changes
cd /var/www/clinical-rnaseq.com
git pull

# Activate virtual environment
source .venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Rebuild frontend
cd prime_vue
npm install
npm run build

# Restart the service
sudo systemctl restart clinical-rnaseq.service
```

### SSL Certificate Renewal

Certbot should automatically renew certificates. You can test the renewal process with:

```bash
sudo certbot renew --dry-run
```

### Monitoring

Check application logs:

```bash
sudo tail -f /var/log/clinical-rnaseq/access.log
sudo tail -f /var/log/clinical-rnaseq/error.log
```
