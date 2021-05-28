python3 manage.py db init; 
python3 manage.py db stamp head; 
python3 manage.py db migrate; 
python3 manage.py db upgrade; 
gunicorn app:app