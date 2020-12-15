#!/bin/sh
set -e
resolver db upgrade
gunicorn -c resolver/gunicorn.py resolver.wsgi:app
