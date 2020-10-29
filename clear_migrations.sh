#!/bin/bash
rm -f apps/*/migrations/0*.py
python3 manage.py makemigrations
python3 manage.py migrate