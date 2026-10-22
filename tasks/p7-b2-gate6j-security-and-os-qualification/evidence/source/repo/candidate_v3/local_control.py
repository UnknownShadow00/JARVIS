"""One bounded request per connected AF_UNIX socket. No listener installation."""
import socket,struct,time
from .contracts import Refused,strict_json,canonical

TOTAL_READ_SECONDS=5.0  # whole-request bound; a trickling peer cannot hold the controller

class LocalControl:
    def __init__(self,runtime,*,operator_uid):
        if type(operator_uid) is not int or operator_uid<0:raise Refused('OPERATOR_UID')
        self.runtime,self.operator_uid=runtime,operator_uid

    def handle(self,connection):
        if connection.family!=socket.AF_UNIX:raise Refused('LOCAL_SOCKET_REQUIRED')
        connection.settimeout(2.0)
        pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        if uid!=self.operator_uid or pid<=0:raise Refused('OPERATOR_PEER')
        deadline=time.monotonic()+TOTAL_READ_SECONDS
        def exact(n):
            data=b''
            while len(data)<n:
                remaining=deadline-time.monotonic()
                if remaining<=0:raise Refused('CONTROL_DEADLINE')
                connection.settimeout(min(2.0,remaining))
                part=connection.recv(n-len(data))
                if not part:raise Refused('CONTROL_TRUNCATED')
                data+=part
            return data
        try:
            length=struct.unpack('!I',exact(4))[0]
            if not 0<length<=20000:raise Refused('CONTROL_LENGTH')
            packet=strict_json(exact(length))
            if type(packet) is not dict or set(packet)!={'body','signature'} or type(packet['body']) is not dict or type(packet['signature']) is not str or len(packet['signature'])>16384:raise Refused('CONTROL_SCHEMA')
            sig=bytes.fromhex(packet['signature']);raw=canonical(packet['body'])
            self.runtime.control(raw,sig,(uid,pid),packet['body'].get('verb'))
            reply=canonical({'accepted':True})
        except Exception:reply=canonical({'accepted':False,'code':'CONTROL_REFUSED'})
        connection.sendall(struct.pack('!I',len(reply))+reply)


class AuthoritySocket:
    """One signed command per connected socket; no listener or signer installed.

    Peer credentials are kernel-extracted; JSON cannot supply a uid or PID.
    Read/checkpoint service transport and production reader wiring remain absent.
    """
    def __init__(self, journal, *, seconds=2):
        if type(seconds) not in (int,float) or not 0 < seconds <= 5:
            raise Refused('AUTHORITY_DEADLINE')
        self.journal, self.seconds = journal, seconds

    def handle(self, connection):
        try:
            if connection.family != socket.AF_UNIX: raise Refused('AUTHORITY_SOCKET')
            pid,uid,_ = struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            if uid != self.journal.authority.peer_uid or pid <= 0: raise Refused('AUTHORITY_PEER')
            end = time.monotonic()+self.seconds
            def exact(n):
                buf = b''
                while len(buf)<n:
                    remaining = end-time.monotonic()
                    if remaining <= 0: raise Refused('AUTHORITY_DEADLINE')
                    connection.settimeout(remaining)
                    part = connection.recv(n-len(buf))
                    if not part: raise Refused('AUTHORITY_TRUNCATED')
                    buf += part
                return buf
            size = struct.unpack('!I',exact(4))[0]
            if not 0 < size <= 20000: raise Refused('AUTHORITY_LENGTH')
            p = strict_json(exact(size))
            if (type(p) is not dict or set(p) != {'body','signature'} or type(p['body']) is not dict
                    or type(p['signature']) is not str or len(p['signature']) != 128):
                raise Refused('AUTHORITY_PACKET')
            body = canonical(p['body']); sig = bytes.fromhex(p['signature'])
            result = self.journal.signed(body,sig,(uid,pid),p['body'].get('verb'))
            reply = canonical({'accepted':True,**result})
        except Exception:
            reply = canonical({'accepted':False,'code':'AUTHORITY_REFUSED'})
        # Also bound response writes; never block an authority on a nonreader.
        connection.settimeout(self.seconds)
        connection.sendall(struct.pack('!I',len(reply))+reply)

# Gate6I accept-based transport. Socket import remains confined to this module.
import array
import os
import stat
import threading
from pathlib import Path
from dataclasses import dataclass
from .storage import no_symlink_ancestors

MAX_FRAME=65536

@dataclass(frozen=True)
class ProcessPin:
    uid: int
    pid: int
    start: str
    boot: str

    @classmethod
    def capture(cls,uid,pid):
        raw=(Path('/proc')/str(pid)/'stat').read_text()
        start=raw[raw.rfind(')')+2:].split()[19]
        boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        return cls(uid,pid,start,boot)

    def verify(self,uid,pid):
        if (uid,pid)!=(self.uid,self.pid) or self.capture(uid,pid)!=self:raise Refused('AUTHORITY_PROCESS_FRESHNESS')


def _socket_path(path,owner):
    path=Path(path);no_symlink_ancestors(path)
    for p in path.parents:
        s=p.lstat(); sticky=s.st_uid==0 and bool(s.st_mode&stat.S_ISVTX)
        if s.st_uid not in (0,owner) or s.st_mode&0o022 and not sticky:raise Refused('AUTHORITY_SOCKET_PARENT')
    s=path.lstat()
    if not stat.S_ISSOCK(s.st_mode) or s.st_uid!=owner or stat.S_IMODE(s.st_mode)!=0o660:raise Refused('AUTHORITY_SOCKET_PATH')
    return (s.st_dev,s.st_ino)


def _exact(sock,n,end,peer=None):
    chunks=[];size=0
    while size<n:
        remaining=end-time.monotonic()
        if remaining<=0:raise Refused('AUTHORITY_DEADLINE')
        sock.settimeout(remaining)
        part,ancillary,flags,_=sock.recvmsg(n-size,socket.CMSG_SPACE(256),getattr(socket,'MSG_CMSG_CLOEXEC',0))
        # Credentials identify each writer, including a passed/inherited connection.
        credentials=[];unexpected=False
        for level,kind,data in ancillary:
            if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                fds=array.array('i');fds.frombytes(data[:len(data)//fds.itemsize*fds.itemsize])
                for fd in fds:os.close(fd)
                unexpected=True
            elif level==socket.SOL_SOCKET and kind==socket.SCM_CREDENTIALS and len(data)==12:
                credentials.append(struct.unpack('3i',data))
            else:unexpected=True
        if unexpected or flags&(socket.MSG_CTRUNC|socket.MSG_TRUNC):raise Refused('AUTHORITY_DESCRIPTORS')
        if peer is not None:
            if len(credentials)!=1 or (credentials[0][1],credentials[0][0])!=peer:raise Refused('AUTHORITY_MESSAGE_PEER')
        elif credentials:raise Refused('AUTHORITY_UNEXPECTED_CREDENTIALS')
        if not part:raise Refused('AUTHORITY_TRUNCATED')
        chunks.append(part);size+=len(part)
    return b''.join(chunks)


def _receive(sock,end,peer=None):
    n=struct.unpack('!I',_exact(sock,4,end,peer))[0]
    if not 0<n<=MAX_FRAME:raise Refused('AUTHORITY_LENGTH')
    return strict_json(_exact(sock,n,end,peer))


def _send(sock,value,end):
    raw=canonical(value)
    if len(raw)>MAX_FRAME:raise Refused('AUTHORITY_RESPONSE_LIMIT')
    left=end-time.monotonic()
    if left<=0:raise Refused('AUTHORITY_DEADLINE')
    sock.settimeout(left);sock.sendall(struct.pack('!I',len(raw))+raw)


class UnixAuthorityServer:
    """Bounded accept loop on a preprovisioned protected directory; no daemon install.

    Separate endpoints and pinned kernel peers enforce roles. No stale socket
    deletion: installer must review cleanup after a crash. Eight workers maximum.
    """
    def __init__(self,path,service,*,channel,peer_pin,seconds=2,group=None):
        if channel not in ('operator','service') or type(peer_pin) is not ProcessPin or type(seconds) not in (int,float) or not 0<seconds<=5:raise Refused('AUTHORITY_LISTENER_CONFIGURATION')
        self.path=Path(path);self.service=service;self.channel=channel;self.pin=peer_pin;self.seconds=seconds
        self.owner=os.geteuid();self.stop_event=threading.Event();self.slots=threading.BoundedSemaphore(8);self.workers=set();self.lock=threading.Lock()
        no_symlink_ancestors(self.path)
        s=self.path.parent.lstat()
        if s.st_uid!=self.owner or stat.S_IMODE(s.st_mode) not in (0o700,0o750):raise Refused('AUTHORITY_LISTENER_DIRECTORY')
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        try:
            # Bind exclusively; never unlink an existing endpoint or follow a link.
            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
            self.sock.bind(str(self.path));os.chmod(self.path,0o660)
            if group is not None:os.chown(self.path,-1,group)
            self.inode=_socket_path(self.path,self.owner)
            self.sock.listen(8);self.sock.settimeout(0.05)
        except BaseException:self.sock.close();raise

    def serve(self):
        while not self.stop_event.is_set():
            try:
                if _socket_path(self.path,self.owner)!=self.inode:break
                conn,_=self.sock.accept()
            except socket.timeout:continue
            except (OSError,Refused):break
            if not self.slots.acquire(blocking=False):conn.close();continue
            t=threading.Thread(target=self._worker,args=(conn,),daemon=True)
            with self.lock:
                if self.stop_event.is_set():conn.close();self.slots.release();break
                self.workers.add(t)
                t.start()

    def _worker(self,conn):
        try:
            end=time.monotonic()+self.seconds
            conn.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,8192)
            try:
                pid,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                self.pin.verify(uid,pid)
                p=_receive(conn,end,(uid,pid))
                self.pin.verify(uid,pid)
                if self.stop_event.is_set() or _socket_path(self.path,self.owner)!=self.inode:raise Refused('AUTHORITY_LISTENER_REPLACED')
                result=self.service.dispatch(self.channel,p,(uid,pid))
                reply={'accepted':True,'result':result}
            except Exception:reply={'accepted':False,'code':'AUTHORITY_REFUSED'}
            try:_send(conn,reply,end)
            except (OSError,Refused):pass
        finally:
            conn.close();self.slots.release()
            with self.lock:self.workers.discard(threading.current_thread())

    def close(self):
        self.stop_event.set();self.sock.close()
        with self.lock:workers=tuple(self.workers)
        end=time.monotonic()+self.seconds+0.1
        for worker in workers:worker.join(max(0,end-time.monotonic()))
        try:
            if _socket_path(self.path,self.owner)==self.inode:self.path.unlink()
        except (OSError,Refused):pass


class UnixAuthorityConnection:
    def __init__(self,path,*,authority_pin,seconds=2):
        if type(authority_pin) is not ProcessPin or type(seconds) not in (int,float) or not 0<seconds<=5:raise Refused('AUTHORITY_CLIENT_CONFIGURATION')
        self.path=Path(path);self.pin=authority_pin;self.seconds=seconds

    def call(self,operation,arguments):
        try:
            inode=_socket_path(self.path,self.pin.uid);end=time.monotonic()+self.seconds
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
                conn.settimeout(self.seconds);conn.connect(str(self.path))
                pid,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                self.pin.verify(uid,pid)
                if _socket_path(self.path,self.pin.uid)!=inode:raise Refused('AUTHORITY_SOCKET_REPLACED')
                _send(conn,dict(version=1,operation=operation,arguments=arguments),end)
                r=_receive(conn,end)
                if type(r) is not dict or set(r)!={'accepted','result'} or r['accepted'] is not True:raise Refused('AUTHORITY_REFUSED')
                self.pin.verify(uid,pid)
                return r['result']
        except Exception:raise Refused('AUTHORITY_UNAVAILABLE_OR_REFUSED') from None


class OperatorCommandClient:
    """No signing API. Caller supplies a separately human-signed fixed-schema body."""
    def __init__(self,connection):self.connection=connection
    def submit(self,raw,signature):
        if type(raw) is not bytes or len(raw)>8192 or type(signature) is not bytes or len(signature)!=64:raise Refused('OPERATOR_PACKET')
        return self.connection.call('SIGNED',dict(body=strict_json(raw),signature=signature.hex()))
