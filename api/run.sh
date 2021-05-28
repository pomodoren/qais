python3 manage.py db init; 
python3 manage.py db stamp head; 
python3 manage.py db migrate; 
python3 manage.py db upgrade; 
gunicorn --bind 0.0.0.0:5000 --workers=5 --threads=2 app:app