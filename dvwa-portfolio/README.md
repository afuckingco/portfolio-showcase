# DVWA Portfolio

A clean, professional portfolio documenting the **Damn Vulnerable Web Application (DVWA)** security research carried out by afuckingco.

## What’s Inside

- **01‑setup** – Docker compose, MariaDB fix script, and step‑by‑step setup guide.
- **02‑reconnaissance** – Network scans, gateway analysis, and raw Nmap results.
- **03‑sql‑injection** – Detailed write‑ups and Python scripts for:
  - UNION‑based injection
  - Boolean‑based blind injection
  - Time‑based blind injection (optimized version)
- **04‑analysis** – Performance comparisons and optimization notes.
- **05‑resources** – Reference list and tools used.

## Quick Start
```bash
# 1. Setup DVWA
cd 01-setup
bash mariadb-fix.sh
python3 setup-dvwa.py

# 2. Run reconnaissance
cd ../02-reconnaissance
bash scan.sh

# 3. Execute injection demos
cd ../03-sql-injection
python3 union_sqli.py
python3 boolean_sqli.py
python3 timebased_sqli.py
```

## License

MIT License – see the `LICENSE` file.

## Contributing

See `CONTRIBUTING.md` for guidelines on how to fork, branch, and submit pull requests.
