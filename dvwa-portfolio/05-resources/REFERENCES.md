# References & Resources

## Official Documentation

### SQL Injection
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP Testing Guide - SQLi](https://owasp.org/www-project-web-security-testing-guide/stable/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)

### Blind SQL Injection
- [PortSwigger: Blind SQL Injection](https://portswigger.net/web-security/sql-injection/blind)
- [HackTricks: SQL Injection - Blind](https://book.hacktricks.xyz/pentesting-web/sql-injection#blind-sql-injection)

### DVWA
- [DVWA GitHub Repository](https://github.com/digininja/DVWA)
- [DVWA Installation Guide](https://github.com/digininja/DVWA/blob/master/README.md)
- [DVWA SQL Injection Walkthrough](https://github.com/digininja/DVWA/wiki/SQL-Injection)

## Tools Used

### Network Reconnaissance
```bash
nmap 7.99                  # Network mapping and port scanning
  -sn                      # Ping scan (host discovery)
  -sV                      # Service version detection
  -A                       # Aggressive scan (OS detection, scripts)
  -oX                      # Output to XML format

curl                       # HTTP requests (UNION-based testing)
openssl s_client          # SSL/TLS certificate inspection
dig / nslookup            # DNS enumeration
```

### Web Application Testing
```bash
Apache2                   # Web server
PHP 7.0+                  # Server-side scripting
MariaDB 11.8.6            # Database server

DVWA                      # Vulnerable application target
```

### Python Libraries
```python
requests          # HTTP client library
BeautifulSoup4    # HTML/XML parsing
time              # Timing-based measurements
sys, re, signal   # Standard library utilities
```

### Code Examples & Cheat Sheets
- [SQLMap Cheat Sheet](https://github.com/sqlmapproject/sqlmap/wiki)
- [SQL Injection Filter Bypass](https://owasp.org/www-community/attacks/xpath_injection)
- [MySQL Functions Reference](https://dev.mysql.com/doc/refman/8.0/en/functions.html)

## Concepts & Theory

### Binary Search Algorithm
- **Time Complexity**: O(log n) vs O(n) for linear search
- **Application**: Fast character extraction in blind SQLi
- **Reference**: [Binary Search - Wikipedia](https://en.wikipedia.org/wiki/Binary_search_algorithm)

### Information Entropy
- **Concept**: Reducing uncertainty through strategic queries
- **Related**: Domain-specific optimization reduces search space
- **Formula**: H(X) = -Σ p(x) log p(x)

### Timing Side-Channels
- **SLEEP() function**: Intentional delay for data extraction
- **BENCHMARK()**: Alternative timing function in MySQL
- **Drawbacks**: Network jitter, server load variability

## Penetration Testing Frameworks

### OWASP
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- **SQLi Ranking**: Currently in Top 10

### NIST
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- Identify → Protect → Detect → Respond → Recover

### PCI DSS
- [PCI-DSS Requirement 6.5.1](https://www.pcisecuritystandards.org/)
- Requirement for SQLi testing in payment card environments

## Certification Paths

### Entry-Level
- **eJPT** (eLearnSecurity Junior Penetration Tester)
  - Includes SQLi module
  - Duration: ~2-3 months
  - Lab practice: DVWA recommended

### Intermediate
- **CEH** (Certified Ethical Hacker)
  - Covers advanced SQLi techniques
  - Duration: ~6 months prep

### Advanced
- **OSCP** (Offensive Security Certified Professional)
  - Hands-on penetration testing
  - SQLi is component of exam
  - Requires practical lab experience

### Specialized
- **GPEN** (GIAC Penetration Tester)
- **GWAPT** (GIAC Web Application Penetration Tester)

## Community Resources

### Forums & Blogs
- [Hack The Box](https://www.hackthebox.eu/) - Vulnerable apps practice
- [TryHackMe](https://www.tryhackme.com/) - Interactive security training
- [PortSwigger Academy](https://portswigger.net/web-security) - Free web security training
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/) - Deliberately insecure application

### YouTube Channels
- [John Hammond](https://www.youtube.com/c/JohnHammond) - Security tutorials
- [IppSec](https://www.youtube.com/c/IppSec) - CTF/pentest walkthroughs
- [LiveOverflow](https://www.youtube.com/c/LiveOverflow) - Binary exploitation & security

### Books
- "The Web Application Hacker's Handbook" - Stuttard & Pinto
- "SQL Injection Attacks and Defense" - Spett & Delahanty
- "The Basics of Web Hacking" - Josh Pauli

## Database-Specific References

### MySQL/MariaDB
- `SUBSTRING(str, pos, len)` - Extract substring
- `ASCII(str)` - Get ASCII value of character
- `IF(condition, true_val, false_val)` - Conditional
- `SLEEP(duration)` - Delay execution
- `GROUP_CONCAT()` - Concatenate multiple rows
- [MySQL Manual](https://dev.mysql.com/doc/)

### Information Schema
```sql
information_schema.TABLES         -- List tables
information_schema.COLUMNS        -- List columns
information_schema.SCHEMATA       -- List databases
information_schema.PROCESSLIST    -- Current queries
```

## Defensive Resources

### Web Application Firewalls (WAF)
- [OWASP ModSecurity](https://github.com/SpiderLabs/ModSecurity)
- [AWS WAF](https://aws.amazon.com/waf/)
- [Cloudflare WAF](https://www.cloudflare.com/waf/)

### Detection Methods
- **Log Analysis**: Look for SQL keywords (UNION, SELECT, IF, SLEEP, BENCHMARK)
- **Rate Limiting**: Flag high request counts from single IP
- **Query Patterns**: Detect unusual sleep times or charset scanning
- **ML-Based**: Anomaly detection in query patterns

### Remediation
1. **Parameterized Queries** (Prepared Statements) - BEST
2. **Input Validation** - Whitelist approach
3. **Output Encoding** - Prevent XSS + Data leakage
4. **Error Handling** - Don't expose SQL errors
5. **Least Privilege** - DB user should only have necessary permissions

## Lab Environment Links

### Quick Setup
```bash
# Clone DVWA
git clone https://github.com/digininja/DVWA.git

# Docker installation (recommended)
docker run -d -p 80:80 -e MYSQL_ROOT_PASSWORD=root vulnerables/web-dvwa

# Manual setup (see SETUP.md)
# ... MariaDB + Apache configuration
```

### Alternative Vulnerable Apps
- **OWASP Juice Shop** - Modern vulnerable web app
- **bWAPP** - Includes 100+ vulnerable functions
- **Mutillidae** - Multi-level vulnerable app
- **WebGoat** - Official OWASP learning platform

## Responsible Disclosure

### Legal Considerations
- Only test on systems you own or have explicit written permission
- Follow local laws and regulations
- Don't access unauthorized accounts or data
- Report vulnerabilities responsibly

### Responsible Disclosure Timeline
1. **Day 1**: Report vulnerability to organization
2. **Day 30**: Follow up if no response
3. **Day 90**: If unfixed, consider public disclosure
4. **Coordination**: Work with vendors to release patches first

## Self-Hosted Lab Notes

**Network**: 192.168.1.0/24  
**Gateway**: 192.168.1.1 (OpenWrt router)  
**Lab Machine**: WSL Kali / Ubuntu 24.04  

**Active Devices**:
- iPhone (iOS 15) × 2
- Samsung A52 (Android)
- Redmi Pad SE (Android)
- Linux development machine

**Caution**: Only conduct testing on lab machines with explicit permission.

---

**Last Updated**: July 4, 2026  
**Maintained By**: Afiq  
**Status**: Active
