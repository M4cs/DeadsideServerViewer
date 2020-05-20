from app.helper.servers import Servers
from json import dumps

servers = Servers()

print(dumps(servers.by_uptime_old()[0], indent=4))