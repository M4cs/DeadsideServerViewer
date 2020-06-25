from flask import Flask, render_template, send_file
from flask_restful import reqparse
from app.helper.servers import Servers, MemServer
from apscheduler.schedulers.background import BackgroundScheduler
from fuzzywuzzy import process
import json

app = Flask(__name__)
m = MemServer()

def search_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('q')
    parser.add_argument('filter')
    return parser

OFFSET = ord('🇦') - ord('A')

def flag(code):
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)

def filter_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('filter')
    return parser

def create_table():
    m.titles = []
    m.serverlist = Servers.populate()
    tables = []
    template = """
                <tr>
                    <th>{index}</th>
                    <td>{name}</td>
                    <td>{uptime}</td>
                    <td>{online}</td>
                    <td>{max}</td>
                    <td>{ip}</td>
                    <td><img src="https://localhost:5000{ratio}"></td>
                </tr>"""
    for index, server in enumerate(m.serverlist):
        if server['addr'] == "92.223.66.100:28600":
            m.sv_info['players'] = server['players']
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
        if server['ratio_num'] == 100:
            ratio = "/assets/full.png"
        elif server['ratio_num'] <= 99 and server['ratio_num'] >= 76:
            ratio = "/assets/medium.png"
        elif server['ratio_num'] <= 75 and server['ratio_num'] >= 46:
            ratio = "/assets/good.png"
        elif server['ratio_num'] <= 45 and server['ratio_num'] > 0:
            ratio = "/assets/low.png"
        else:
            ratio = "/assets/empty.png"
        if server['addr'] == "92.223.66.100:28600":
            m.sv_info['capacity'] = "https://deadsidesv.com/" + ratio
        tables.append(template.format(index=index, name=server['id'].replace('_', ' ').replace('*', ''), uptime=uptime, online=server['players'], max=server['playersmax'], ip=server['addr'], ratio=ratio))
    return tables

def update_cache():
    old_tables = m.tables
    m.tables = create_table()
    if len(m.tables) == 0:
        m.tables = old_tables
    
    
update_cache()

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_cache, trigger="interval", seconds=60)
scheduler.start()

@app.route('/')
def index():
    parser = filter_parser()
    args = parser.parse_args()
    if args['filter'] != "+players":
        serverlist = Servers.populate_filter(m.serverlist, args['filter'])
        tables = []
        template = """
                <tr>
                    <th>{index}</th>
                    <td>{name}</td>
                    <td>{uptime}</td>
                    <td>{online}</td>
                    <td>{max}</td>
                    <td>{ip}</td>
                    <td><img src="{ratio}"></td>
                </tr>"""
        for index, server in enumerate(serverlist):
            if server['addr'] == "92.223.66.100:28600":
                m.sv_info['players'] = server['players']
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
            if server['ratio_num'] >= 100:
                ratio = "/assets/full.png"
            elif server['ratio_num'] <= 99 and server['ratio_num'] >= 76:
                ratio = "/assets/medium.png"
            elif server['ratio_num'] <= 75 and server['ratio_num'] >= 46:
                ratio = "/assets/good.png"
            elif server['ratio_num'] <= 45 and server['ratio_num'] > 0:
                ratio = "/assets/low.png"
            else:
                ratio = "/assets/empty.png"
            if server['addr'] == "92.223.66.100:28600":
                m.sv_info['capacity'] = "https://deadsidesv.com/" + ratio
            m.titles.append(server['id'])
            tables.append(template.format(index=index, name=server['id'].replace('_', ' ').replace('*', ''), uptime=uptime, online=server['players'], max=server['playersmax'], ip=server['addr'], ratio=ratio))
        return render_template('index.html', tables=tables, filter=args['filter']), 200
    else:
        return render_template('index.html', tables=m.tables, filter=args['filter']), 200
    
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
            tables.append(template.format(index=index, name=server['id'].replace('_', ' ').replace('*', ''), uptime=uptime, online=server['players'], max=server['playersmax'], ip=server['addr']))
    return render_template('index.html', tables=tables, filter=args['filter'], sv_players=m.sv_info['players'], sv_capacity=m.sv_info['capacity']), 200