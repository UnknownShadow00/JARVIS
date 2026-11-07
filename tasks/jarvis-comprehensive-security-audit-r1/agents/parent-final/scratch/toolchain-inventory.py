import sys,json,sqlite3,ssl
from importlib import metadata
names=['fastapi','starlette','httpx','pydantic','pydantic-settings','PyYAML','pytest','pytest-asyncio','psutil','APScheduler','numpy']
versions={}
for n in names:
    try:versions[n]=metadata.version(n)
    except metadata.PackageNotFoundError:versions[n]=None
print(json.dumps({'scope':'audit toolchain only; not deployed package evidence','python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version,'openssl':ssl.OPENSSL_VERSION,'packages':versions},sort_keys=True))
