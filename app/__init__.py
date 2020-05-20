from flask import Flask, render_template, send_file
from flask_restful import reqparse
from app.helper.servers import Servers, MemServer
from apscheduler.schedulers.background import BackgroundScheduler
from fuzzywuzzy import process
import redis
import json

app = Flask(__name__)
m = MemServer()

def search_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('q')
    return parser

def create_table():
    m.titles = []
    serverlist = Servers.populate()
    tables = []
    template = """
                <tr>
                    <th>{index}</th>
                    <td>{name}</td>
                    <td>{uptime}</td>
                    <td>{online}</td>
                    <td>{max}</td>
                    <td>{ip}</td>
                </tr>"""
    for index, server in enumerate(serverlist):
        index += 1
        days, hours, minutes = MemServer.days_hours_minutes(server['starttime'])
        uptime = ""
        if int(days) > 0:
            uptime = days + " days "
        if int(hours) > 0:
            uptime = uptime + hours + " hrs. "
        if int(minutes) > 0:
            uptime = uptime + minutes + " min."
        uptime = uptime.strip()
        if uptime.endswith(','):
            uptime = uptime[0:-1]
        m.titles.append(server['id'])
        tables.append(template.format(index=index, name=server['id'].replace('_', ' ').replace('*', ''), uptime=uptime, online=server['players'], max=server['playersmax'], ip=server['addr']))
    return tables

def update_cache():
    m.tables = create_table()
    
update_cache()

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_cache, trigger="interval", seconds=60)

@app.route('/')
def index():
    print(len(m.tables))
    return render_template('index.html', tables=m.tables), 200
    
@app.route('/assets/<file>')
def serve(file):
    return send_file('templates/assets/' + file), 200

@app.route('/search')
def search():
    serverlist = Servers.populate()
    parser = search_parser()
    args = parser.parse_args()
    search = args['q']
    results = process.extract(search, m.titles)
    res = []
    for result in results:
        res.append(result[0])
    print(res)
    tables = []
    template = """
                <tr>
                    <th>{index}</th>
                    <td>{name}</td>
                    <td>{uptime}</td>
                    <td>{online}</td>
                    <td>{max}</td>
                    <td>{ip}</td>
                </tr>"""
    for index, server in enumerate(serverlist):
        if server['id'] in res:
            index += 1
            days, hours, minutes = MemServer.days_hours_minutes(server['starttime'])
            uptime = ""
            if days:
                uptime = days + " days, "
            if hours:
                uptime = hours + " hrs., "
            if minutes:
                uptime = minutes + " min."
            uptime = uptime.strip()
            if uptime.endswith(','):
                uptime = uptime[0:-1]
            m.titles.append(server['id'].replace('*', ' ').replace('_', ' '))
            tables.append(template.format(index=index, name=server['id'].replace('_', ' ').replace('*', ''), uptime=uptime, online=server['players'], max=server['playersmax'], ip=server['addr']))
    return render_template('index.html', tables=tables), 200