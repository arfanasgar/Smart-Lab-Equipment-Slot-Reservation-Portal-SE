
# Lab 5 – Static Code Analysis

## Issues Identified and Fixes Applied

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Unsafe shell execution (B605) | Security – High | 71 | os.system() executes a command through a shell and may allow command injection. | Replaced with subprocess.run() using an argument list and check=True. |
| Insecure temporary file (B306) | Security – Medium | 66 | tempfile.mktemp() creates an insecure temporary file path. | Replaced with tempfile.NamedTemporaryFile(). |
| Hardcoded password (B105) | Security – Low | 6 | A referee password was stored directly in the source code. | Removed the hardcoded password. |
| Mutable default argument (W0102) | Bug | 11 | Using players=[] could share a mutable list between function calls. | Changed the default to None and initialized a new list inside the function. |
| Insecure random generator (B311) | Security – Low | 61 | random.choice() uses a standard pseudo-random generator. | Replaced with secrets.choice(). |
| Naming convention violations | Code quality | Multiple | Function and argument names did not follow snake_case conventions. | Renamed functions and arguments using snake_case. |
| Missing docstrings | Code quality | Multiple | Functions lacked descriptive documentation. | Added appropriate docstrings. |
| Formatting violations | Style | 5, 60, 79, 87 | Flake8 reported whitespace, blank-line and comment-spacing violations. | Corrected formatting according to PEP 8. |

## Conclusion

Static code analysis helped identify programming mistakes, security vulnerabilities and formatting issues. Pylint improved code quality, Bandit helped identify security risks, and Flake8 improved readability and consistency.

All identified issues were addressed, and the final code was rechecked using all three tools.
