#!/usr/bin/env bash
# Render.com build bosqichi (prod). render.yaml -> buildCommand: "bash build.sh".
set -o errexit

pip install -r requirements.txt

# Statik fayllarni yig'ish (WhiteNoise) va migratsiyalar.
python manage.py collectstatic --no-input
python manage.py migrate
