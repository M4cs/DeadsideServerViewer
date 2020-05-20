[program:deadsideserverviewer]
directory=/home/max/DeadsideServerViewer
command=/home/max/DeadsideServerViewer/.flaskapp/bin/uwsgi --http :8910 --file ./app.py --callable app
autostart=true
autorestart=true
stderr_logfile=/home/max/DeadsideServerViewer/DeadsideServerViewer.err.log
stdout_logfile=/home/max/DeadsideServerViewer/DeadsideServerViewer.out.log