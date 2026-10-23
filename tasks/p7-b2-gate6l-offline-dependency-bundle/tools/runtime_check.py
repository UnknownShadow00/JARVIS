"""Offline non-generating validation. Never imports operational OS tools or providers."""
import ctypes,hashlib,importlib.metadata,json,pathlib,platform,sqlite3,sys
def distribution_set(rows):
    import re
    result={}
    for name,version in rows:
        name=re.sub(r'[-_.]+','-',name).lower()
        if name in result:raise ValueError('DUPLICATE_DISTRIBUTION')
        result[name]=version
    return result
def check_versions(pins,actual,python,sqlite,machine):
    if machine!='x86_64':raise ValueError('WRONG_ARCHITECTURE')
    if tuple(python)!=(3,14,4):raise ValueError('WRONG_PYTHON')
    if sqlite!='3.46.1':raise ValueError('WRONG_SQLITE')
    if actual!=pins:raise ValueError('DISTRIBUTION_SET_MISMATCH')
def check_library_origins(mappings,root):
    for library in ('libsqlite3.so','libseccomp.so','libcrypto.so','libssl.so'):
        paths=[p for p in mappings if pathlib.Path(p).name.startswith(library)]
        if not paths or any(not pathlib.Path(p).is_relative_to(root) for p in paths):raise ValueError('MISSING_OR_HOST_LIBRARY '+library)
def main():
    base=pathlib.Path(__file__).resolve().parents[1]
    # This controlled addition is only the freshly constructed private fixture.
    site=base/'work/mixed-env-r2/lib/python3.14/site-packages'
    sys.path.insert(0,str(site));sys.path.insert(0,str(base/'tools'))
    from offline_exec import deny_network
    deny_network()
    pins=json.loads((base/'locks/dependency-versions.json').read_text())['packages']
    norm=lambda n:n.lower().replace('_','-').replace('.','-')
    actual=distribution_set((d.metadata['Name'],d.version) for d in importlib.metadata.distributions(path=[str(site)]))
    expected={norm(n):v for n,v in pins.items()}
    check_versions(expected,actual,sys.version_info[:3],sqlite3.sqlite_version,platform.machine())
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key=Ed25519PrivateKey.generate();sig=key.sign(b'offline synthetic test');key.public_key().verify(sig,b'offline synthetic test')
    # Ephemeral key remains in process memory; no secret output or storage.
    import fastapi,numpy,pydantic
    lib=ctypes.CDLL('libseccomp.so.2')
    class Version(ctypes.Structure):_fields_=[('major',ctypes.c_uint),('minor',ctypes.c_uint),('micro',ctypes.c_uint)]
    lib.seccomp_version.restype=ctypes.POINTER(Version);v=lib.seccomp_version().contents
    mappings=sorted({line.split()[-1] for line in open('/proc/self/maps') if '/' in line and any(s in line for s in ('libsqlite','libseccomp','libcrypto','libssl','_rust','_cffi'))})
    check_library_origins(mappings,base/'work/downloaded-runtime/usr/lib/x86_64-linux-gnu')
    if pathlib.Path(sys.prefix)!=base/'work/downloaded-runtime/usr':raise ValueError('HOST_INTERPRETER_FALLBACK')
    print(json.dumps({'status':'PASS','distributions':len(actual),'exact_versions':True,'python':platform.python_version(),
      'sqlite':sqlite3.sqlite_version,'cryptography':actual['cryptography'],'seccomp':f'{v.major}.{v.minor}.{v.micro}',
      'ed25519':'synthetic sign/verify PASS','core_imports':['fastapi','numpy','pydantic'],
      'network':'kernel non-AF_UNIX sockets denied','mapped_libraries':mappings,'prefix':sys.prefix},indent=2))
if __name__=='__main__':main()
