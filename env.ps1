if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

pip install --upgrade pip

if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt
}
