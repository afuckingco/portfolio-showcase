# Contributing to dvwa-portfolio

We welcome contributions! Please follow these guidelines to keep the project consistent and maintainable.

## How to contribute

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/dvwa-portfolio.git
   cd dvwa-portfolio
   ```
3. **Create a new branch** for your work:
   ```bash
   git checkout -b my-feature-branch
   ```
4. **Make your changes** – keep the code style consistent (see the CI workflow that runs `black` and `flake8`).
5. **Commit your changes** with a clear, concise message.
6. **Push the branch** to your fork:
   ```bash
   git push origin my-feature-branch
   ```
7. **Open a Pull Request** on the original `afuckingco/dvwa-portfolio` repository.
   - Target the `main` branch.
   - Ensure the CI checks pass before requesting review.

## Code style

- Python files should be formatted with **black** and pass **flake8**.
- Use meaningful variable and function names.
- Add or update documentation in the relevant `README` sections.

## Testing

If you add new scripts or modify existing ones, ensure they run without errors. You can verify locally by executing the scripts in the `03-sql-injection` folder.

## Reporting issues

- Use GitHub Issues for bugs or feature requests.
- Provide a clear description, steps to reproduce (if applicable), and any relevant logs.

Thank you for helping improve this portfolio!
