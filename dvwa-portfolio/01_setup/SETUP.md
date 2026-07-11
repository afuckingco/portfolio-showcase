# DVWA Setup & Infrastructure Guide

## Environment

- **OS**: Kali Linux / Ubuntu 24.04 LTS on WSL
- **Web Server**: Apache2 / lighttpd
- **Database**: MariaDB 11.8.6
- **PHP**: 7.0+
- **Application**: DVWA (Damn Vulnerable Web Application)

## Prerequisites

```bash
sudo apt update
sudo apt install apache2 php php-mysql mariadb-server curl
sudo a2enmod php7.0
```

## Critical Issue: MariaDB Startup Failure

### Symptom
```
ERROR: Cannot create /run/mysqld/wsrep-start-position: Directory nonexistent
mariadb.service: Control process exited, code=exited status=1
```

### Root Cause
In WSL/containers, `/run` is a tmpfs that resets on reboot. MariaDB needs `/run/mysqld/` directory to exist.

### Solution

**Step 1**: Create and fix ownership
```bash
sudo mkdir -p /run/mysqld
sudo chown mysql:mysql /run/mysqld
```

**Step 2**: Start MariaDB
```bash
sudo service mariadb start
```

**Step 3**: Verify startup
```bash
sudo journalctl -xeu mariadb.service --no-pager | tail -5
# Should show: "ready for connections"
```

**Step 4** (Optional): Make persistent across WSL reboots

Create `/etc/rc.local` (if doesn't exist):
```bash
sudo nano /etc/rc.local
```

Add:
```bash
#!/bin/bash
mkdir -p /run/mysqld
chown mysql:mysql /run/mysqld
/usr/sbin/mariadbd --user=mysql &
```

Make executable:
```bash
sudo chmod +x /etc/rc.local
```

## DVWA Installation

### Download & Extract
```bash
cd /var/www/html
sudo git clone https://github.com/digininja/DVWA.git dvwa
cd dvwa
cp config/config.inc.php.dist config/config.inc.php
```

### Database Configuration

Edit `config/config.inc.php`:
```php
$_DVWA = array();

// Database
$_DVWA[ 'db_server' ]   = '127.0.0.1';
$_DVWA[ 'db_database' ] = 'dvwa';
$_DVWA[ 'db_user' ]     = 'app';
$_DVWA[ 'db_password' ] = 'password';
$_DVWA[ 'db_port' ]     = '3306';
```

### File Permissions
```bash
sudo chown -R www-data:www-data /var/www/html/dvwa
sudo chmod -R 755 /var/www/html/dvwa
```

## Initial Database Setup via Browser

1. Navigate to `http://localhost/dvwa/setup.php`
2. Check prerequisites checklist (should all be green)
3. Click **"Create / Reset Database"**
4. Should see: `Database already exists. Resetting DB...`

### If Setup Fails

Check checklist items for red (✗):
- `PHP module pdo_mysql` - If missing: `sudo apt install php-pdo php-mysql`
- `config.inc.php` writable - If missing: `sudo chown www-data config/config.inc.php`
- MySQL connection - Verify with: `mysql -u app -p -h 127.0.0.1 -e "SELECT 1"`

## Verify Database Creation

```bash
# Connect as app user
mysql -u app -p -h 127.0.0.1
Enter password: password

# Inside mysql prompt
USE dvwa;
SHOW TABLES;
SELECT user, password FROM users;
```

Expected output (users table):
```
user     | password (MD5 hash)
---------+----------------------------------
admin    | 5f4dcc3b5aa765d61d8327deb882cf99
user     | e99a18c428cb38d5f260853678922e03
gordonb  | e0ba6b9b541e4b0b4ef3522ec26dc406
...
```

## Login to DVWA

1. Browse to `http://localhost/dvwa/`
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `password`

3. Set security level to **Low** (or Medium/High for blind SQLi)
   - Navigate to DVWA Security → Low

## Troubleshooting

### Issue: "404 Not Found" after setup
- Check Apache2 is running: `sudo systemctl status apache2`
- Enable mod_rewrite if needed: `sudo a2enmod rewrite`
- Restart Apache: `sudo systemctl restart apache2`

### Issue: "Connection refused" when running scripts
- Check web server is listening: `curl -I http://localhost/`
- Check MariaDB is running: `sudo systemctl status mariadb`

### Issue: "Access denied for user 'app'" in scripts
- Verify app user exists: `mysql -u app -p -h 127.0.0.1 -e "SELECT 1"`
- Reset password: `mysql -u root -p -e "ALTER USER 'app'@'127.0.0.1' IDENTIFIED BY 'password'"`

## Persistent Setup Script

Save as `mariadb-fix.sh`:
```bash
#!/bin/bash
# Auto-fix MariaDB on WSL startup

echo "[*] Ensuring /run/mysqld exists..."
sudo mkdir -p /run/mysqld
sudo chown mysql:mysql /run/mysqld

echo "[*] Starting MariaDB..."
sudo service mariadb start

echo "[*] Verifying database..."
mysql -u app -p"password" -h 127.0.0.1 -e "USE dvwa; SELECT COUNT(*) FROM users;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "[+] MariaDB and DVWA ready!"
else
    echo "[-] Database connection failed"
    exit 1
fi
```

Run before starting exploitation:
```bash
bash mariadb-fix.sh
```
