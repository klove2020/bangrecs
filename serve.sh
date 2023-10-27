uwsgi --socket 127.0.0.1:3031 --wsgi-file serve.py --callable app --stats 127.0.0.1:9191 --processes 2 --threads 4
