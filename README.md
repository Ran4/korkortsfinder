# Installing

```bash
# 1. Manually install the chromedriver and put it in the root folder next to `find_korkort.py`

python3 -m venv .venv
. .venv/bin/activate && pip install -r requirements.txt
```

# Setup

```bash
cp .example.env .env
# Now modify .env with gmail username/password and target email
```

# Running

```bash
. .venv/bin/activate && python3 find_korkort.py
```
