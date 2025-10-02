if not test -d ".venv"
    python3.11 -m venv .venv
end

source .venv/bin/activate.fish

pip install --upgrade pip; or true

if test -f "requirements-dev.txt"
    pip install -r requirements-dev.txt; or true
end
