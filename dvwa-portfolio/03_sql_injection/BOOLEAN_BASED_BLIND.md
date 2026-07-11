Boolean-Based Blind SQL Injection

Speed        : ~60-120 seconds for full MD5 hash
Requests/char: 36 (full alphanumeric) or 16 (hex-aware)
Detectability: Medium (no SLEEP keyword, but high request count)

Overview

Boolean blind works when the application behaves differently for
TRUE vs FALSE conditions -- e.g. row present vs absent, different
HTML block rendered, different redirect, different status code.

DVWA Low/Medium security on /vulnerabilities/sqli/?id=
returns the user record when the condition is TRUE, and shows
"User ID is missing" body when FALSE.

Payload Template

  1' AND (SELECT ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),<pos>,1))) = <code>--

  -  ASCII(letter) values:
       '0'-'9' = 48-57
       'a'-'f' = 97-102 (hex subset)
       full =  32-126 (printable)

  - Inject via GET: id= payload (URL-encoded spaces as + or %20)

Mapping TRUE vs FALSE

  TRUE  -> body contains "First name: admin" (or similar row)
  FALSE -> "User ID is missing in input."

  Strict regex check (recommended):
    re.search(r'<pre>First name:', body) is True
    else False

Extraction Strategy (Hex-Optimized)

  Same domain-knowledge shortcut as the time-based script:
    - target is MD5 (32 hex chars)
    - charset 0-9a-f only (16 values)
    - 32 chars * 16 = 512 requests worst-case linear
    - binary search every char: 32 * 4 = 128 requests best-case

  See: boolean_sqli.py for the automated implementation.

DVWA Security Level Compatibility

  Low    : id is reflected raw, no filter. Works directly.
  Medium : id pulled from form select (numeric only) -- you cannot inject
           quotes here. UNION-based still works, but boolean blind
           degrades to numeric comparison only.
  High   : separate input page, payload reflected via session. The
           actual query is still injectable when you submit. Use this
           level to practice blind techniques.

Detection Signatures

  - Repeated numeric comparison in id parameter
  - High request rate from same IP (>50 req/min)
  - Pattern: id=1' AND (SELECT ASCII(SUBSTRING(... =NN--

Defense

  1. Parameterized queries (primary)
  2. Generic error messages (no TRUE/FALSE signal)
  3. Rate limiting per session
  4. WAF rules: SUBSTRING + ASCII patterns

References

  - PortSwigger: Blind SQLi
    https://portswigger.net/web-security/sql-injection/blind
  - OWASP Testing Guide
    https://owasp.org/www-project-web-security-testing-guide/
