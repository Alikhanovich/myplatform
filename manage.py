#!/usr/bin/env python
"""Django'ning buyruq qatori vositasi (administrativ vazifalar uchun)."""
import os
import sys


def main():
    # Lokal dev sukut bo'yicha. Prod'da DJANGO_SETTINGS_MODULE env orqali
    # config.settings.prod ga o'rnatiladi (render.yaml / build.sh).
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django import qilinmadi. Virtual muhit faollashganmi va "
            "`pip install -r requirements.txt` bajarilganmi tekshiring."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
