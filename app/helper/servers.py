import requests, json, time
from datetime import timedelta
class MemServer:
    def __init__(self):
        self.tables = []
        self.titles = []
    
    @staticmethod
    def days_hours_minutes(up):
        td = timedelta(seconds=int(time.time()) - int(up))
        return str(td.days), str(td.seconds//3600), str((td.seconds//60)%60)

                
        
        

class Servers:
    
    @staticmethod  
    def populate():
        serverlist = []
        r = requests.get('http://176.57.174.169/dsapi/serverlist').json()
        r2 = requests.get('http://51.89.1.248/dsapi/serverlist').json()
        if r.get('serverlist') and r2.get('serverlist'):
            serverlist = r['serverlist']
            for x in r2['serverlist']:
                serverlist.append(x)
        x = []
        for s in serverlist:
            if any(d['addr'] == s['addr'] for d in x):
                pass
            else:
                x.append(s)
        return sorted(x, key = lambda i: i['players'], reverse=True)