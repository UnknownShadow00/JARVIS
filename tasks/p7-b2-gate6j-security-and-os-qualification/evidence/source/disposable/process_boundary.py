"""Fresh role processes and bounded, non-executable JSON control pipes."""
import dataclasses,json,math,multiprocessing,os,select,struct,time

LIMIT=65536

def role_context():return multiprocessing.get_context('spawn')

def encode(value,depth=0):
    if depth>32:raise ValueError('IPC_DEPTH')
    if value is None or type(value) in (str,bool,int,float):return value
    if type(value) is bytes:return {'__g6j_type__':'bytes','value':value.hex()}
    if type(value) is tuple:return {'__g6j_type__':'tuple','value':[encode(v,depth+1) for v in value]}
    if type(value) is list:return [encode(v,depth+1) for v in value]
    if type(value) is dict:
        if any(type(k) is not str for k in value) or '__g6j_type__' in value:raise ValueError('IPC_KEYS')
        return {k:encode(v,depth+1) for k,v in value.items()}
    if dataclasses.is_dataclass(value) and type(value).__module__=='candidate_v3.contracts' and type(value).__name__ in ('Bindings','StepContract','Resource','Limits'):
        return {'__g6j_type__':type(value).__name__,'value':{f.name:encode(getattr(value,f.name),depth+1) for f in dataclasses.fields(value)}}
    raise ValueError('IPC_TYPE')

def decode(value,depth=0):
    if depth>32:raise ValueError('IPC_DEPTH')
    if type(value) is list:return [decode(v,depth+1) for v in value]
    if type(value) is not dict:return value
    if '__g6j_type__' not in value:return {k:decode(v,depth+1) for k,v in value.items()}
    if set(value)!={'__g6j_type__','value'}:raise ValueError('IPC_TAG')
    tag=value['__g6j_type__'];v=value['value']
    if tag=='bytes' and type(v) is str:return bytes.fromhex(v)
    if tag=='tuple' and type(v) is list:return tuple(decode(x,depth+1) for x in v)
    if tag in ('Bindings','StepContract','Resource','Limits') and type(v) is dict:
        from candidate_v3.contracts import Bindings,StepContract,Resource,Limits
        cls={'Bindings':Bindings,'StepContract':StepContract,'Resource':Resource,'Limits':Limits}[tag]
        if set(v)!={f.name for f in dataclasses.fields(cls)}:raise ValueError('IPC_FIELDS')
        return cls(**{k:decode(x,depth+1) for k,x in v.items()})
    raise ValueError('IPC_TAG')

class SafePipe:
    """Never Connection.recv()/pickle from a lower-privilege role. Total deadline."""
    def __init__(self,connection,seconds=20):self.connection=connection;self.seconds=seconds
    def close(self):self.connection.close()
    def poll(self,seconds):return bool(select.select([self.connection.fileno()],[],[],seconds)[0])
    def _transfer(self,payload=None):
        fd=self.connection.fileno();os.set_blocking(fd,False);end=time.monotonic()+self.seconds
        def wait(write=False):
            left=end-time.monotonic()
            if left<=0 or not any(select.select([] if write else [fd],[fd] if write else [],[],left)[:2]):raise TimeoutError('IPC_DEADLINE')
        if payload is not None:
            body=struct.pack('!I',len(payload))+payload
            while body:
                wait(True)
                try:n=os.write(fd,body)
                except BlockingIOError:continue
                if not n:raise EOFError('IPC_CLOSED')
                body=body[n:]
            return
        def exact(n):
            chunks=[];size=0
            while size<n:
                wait()
                try:part=os.read(fd,n-size)
                except BlockingIOError:continue
                if not part:raise EOFError('IPC_CLOSED')
                chunks.append(part);size+=len(part)
            return b''.join(chunks)
        length=struct.unpack('!I',exact(4))[0]
        if not 0<length<=LIMIT:raise ValueError('IPC_LENGTH')
        return exact(length)
    def send(self,value):
        raw=json.dumps(encode(value),allow_nan=False,separators=(',',':')).encode()
        if len(raw)>LIMIT:raise ValueError('IPC_LENGTH')
        self._transfer(raw)
    def recv(self):
        def pairs(items):
            result={}
            for k,v in items:
                if k in result:raise ValueError('IPC_DUPLICATE')
                result[k]=v
            return result
        def reject(_):raise ValueError('IPC_NUMBER')
        def finite(text):
            value=float(text)
            if not math.isfinite(value):raise ValueError('IPC_NUMBER')
            return value
        return decode(json.loads(self._transfer(),object_pairs_hook=pairs,parse_constant=reject,parse_float=finite))
