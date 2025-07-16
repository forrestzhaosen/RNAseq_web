# Deployment Guide for clinical-rnaseq.com

This guide provides comprehensive instructions for deploying the Clinical RNA-seq Data Viewer on your domain.

## Prerequisites

- A server running Ubuntu/Debian (adjust commands accordingly for other distributions)
- Domain name (clinical-rnaseq.com) with DNS configured to point to your server
- Basic knowledge of Linux commands and server administration

## 1. Initial Server Setup

### Install Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
```

### Install Node.js (if not already installed)

```bash
# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

## 2. Application Setup

### Set Up Python Environment

```bash
# Navigate to your project directory
cd ~/RNAseq_web

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Build Vue.js Frontend

```bash
# Navigate to frontend directory
cd ~/RNAseq_web/prime_vue

# Install dependencies and build
npm install
npm run build
```

This will create a `dist` folder with optimized static files.

## 3. Configure Web Server

### Set Up Initial HTTP-only Nginx Configuration

```bash
# Copy the Nginx config to the proper location
sudo cp ~/RNAseq_web/nginx_config.conf /etc/nginx/sites-available/clinical-rnaseq.com

# Create a symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/clinical-rnaseq.com /etc/nginx/sites-enabled/

# Create directory for certbot verification if needed
sudo mkdir -p /var/www/html

# Test the configuration
sudo nginx -t

# If the test passes, restart Nginx
sudo systemctl restart nginx
```

### Create a Log Directory for Your Application

```bash
# Create log directory with proper permissions
sudo mkdir -p /var/log/clinical-rnaseq
sudo chown ubuntu:ubuntu /var/log/clinical-rnaseq  # Change 'ubuntu' to your username
```

## 4. Set Up Application Service

```bash
# Copy the systemd service file
sudo cp ~/RNAseq_web/systemd_service.service /etc/systemd/system/clinical-rnaseq.service

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable clinical-rnaseq.service

# Start the service
sudo systemctl start clinical-rnaseq.service

# Check the status to make sure it's running
sudo systemctl status clinical-rnaseq.service
```

## 5. Obtain SSL Certificate

```bash
# Make sure ports 80 and 443 are open
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Obtain SSL certificate
sudo certbot --nginx -d clinical-rnaseq.com -d www.clinical-rnaseq.com
```

Answer the prompts from Certbot. When asked if you want to redirect HTTP to HTTPS, select "2" to enable the redirect.

## 6. Verify Everything is Working

Visit your website at https://clinical-rnaseq.com to make sure it loads correctly.

Check the API endpoints by visiting https://clinical-rnaseq.com/api/health

## Troubleshooting

### If Nginx Fails to Start

```bash
# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify configuration
sudo nginx -t
```

### If Flask App Fails to Start

```bash
# Check the service logs
sudo journalctl -u clinical-rnaseq.service

# Check if Gunicorn is running
ps aux | grep gunicorn

# Check gunicorn error logs
tail -f /var/log/clinical-rnaseq/error.log
```

### If SSL Certificate Fails to Obtain

```bash
# Make sure port 80 is open and not blocked by a firewall
sudo ufw status

# Check Certbot logs
sudo certbot --nginx -d clinical-rnaseq.com --dry-run
```

### If Frontend Files Are Not Found

Ensure the Vue.js files are built and in the correct location:

```bash
# Check if the dist directory exists and has files
ls -la ~/RNAseq_web/prime_vue/dist

# Make sure Nginx has permission to read these files
sudo chown -R www-data:www-data ~/RNAseq_web/prime_vue/dist
```

## Maintenance

### Updating the Application

```bash
# Pull the latest changes
cd ~/RNAseq_web
git pull

# Update backend dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Rebuild the frontend
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

### Viewing Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Flask application logs
sudo journalctl -u clinical-rnaseq.service -f

# Gunicorn logs
tail -f /var/log/clinical-rnaseq/access.log
tail -f /var/log/clinical-rnaseq/error.log
```

## Backing Up Your Application

### Database Backup

```bash
# Create a backup directory
mkdir -p ~/backups

# Copy SQLite database files
cp ~/RNAseq_web/data/*.db ~/backups/

# Compress the backup
tar -czvf ~/backups/rnaseq-db-backup-$(date +%Y%m%d).tar.gz ~/backups/*.db
```

### Full Application Backup

```bash
# Backup the entire application directory
tar -czvf ~/backups/rnaseq-full-backup-$(date +%Y%m%d).tar.gz ~/RNAseq_web
```

## Security Considerations

1. **Set Up a Firewall**:
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. **Set Up Fail2Ban** (optional but recommended):
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

3. **Keep Your System Updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## Final Notes

After deployment, regularly check your logs for any issues or unusual activity. Monitor server resources (CPU, memory, disk) to ensure optimal performance. Consider setting up monitoring tools like Prometheus/Grafana or a simpler tool like Netdata for real-time server monitoring.

Keep regular backups of your database files, especially if they contain important data.
