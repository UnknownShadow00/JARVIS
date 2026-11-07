"""Root-private persistent session registry and hash-chained evidence journal.

No deletion. Nonblocking exclusive control lock; immutable plans and phase claims;
append+fsync events; incomplete setup is a tombstone, never a fresh empty session.
"""
import copy
import fcntl
import os
from pathlib import Path
import stat
from model import Busy,Refusal,canonical,need,names,parse,sha
CONTROL={'PREPARING','ARMED','START_REQUESTED','START_UNKNOWN_KEEP_FENCE','ACTIVE',
         'SETUP_FAILED_NO_START','STOPPED_OBSERVED','TERMINATION_UNPROVEN','CLOSING','CLOSED',
         'POLICY_A_BLOCKER_NO_FORCE','POST_ACTION_OBSERVATION_FAILED','IDENTITY_OR_INTERFACE_BLOCKER'}

class MemoryStore:
    def __init__(self):
        self.p=None;self.events=[];self.claims=set();self.inflight=set();self.attempts={};self.history=[];self.healthy=True;self.fail_write=False;self.armed=False;self.used_approvals=set()
    def create(self,p):
        need(self.p is None,'session_already_reserved')
        need(p['approval_sha256'] not in self.used_approvals,'approval_already_consumed')
        self.used_approvals.add(p['approval_sha256']);self.p=copy.deepcopy(p)
        self.event('PREPARING',{})
    def bind(self,session):need(self.p['session']==session,'active_generation_changed')
    def assert_workers_idle(self):need(not self.inflight,'worker_still_in_flight')
    def plan(self):need(self.p is not None,'no_session');return copy.deepcopy(self.p)
    def event(self,kind,data):
        if self.fail_write:self.healthy=False;raise OSError('fixture_evidence_failure')
        self.events.append({'kind':kind,'data':copy.deepcopy(data)})
        if kind=='ARMED':self.armed=True
    def is_armed(self):return self.armed
    def best_effort(self,kind,data):
        try:self.event(kind,data)
        except OSError:self.healthy=False
    def phase(self):
        if any(r['kind']=='CLOSED' for r in self.events):return 'CLOSED'
        return next((r['kind'] for r in reversed(self.events) if r['kind'] in CONTROL),'PREPARING')
    def claim(self,phase):
        if self.phase() in ('CLOSED','CLOSING'):return False
        if phase in self.claims:return False
        if phase in self.inflight:raise Busy('phase_worker_busy')
        need(self.attempts.get(phase,0)<2,'bounded_action_attempts_exhausted')
        if self.fail_write:self.healthy=False;raise OSError('claim_write_failure')
        self.attempts[phase]=self.attempts.get(phase,0)+1;self.inflight.add(phase);return True
    def release(self,phase,terminal):
        self.inflight.discard(phase)
        if terminal:self.claims.add(phase)
    def retire(self):
        self.history.append((self.p,self.events));self.p=None;self.events=[];self.claims=set();self.inflight=set();self.attempts={};self.armed=False


def bounded_read(path,limit=2*1024*1024):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=limit,'unsafe_state_file')
        b=os.read(fd,limit+1);after=os.fstat(fd)
        need(len(b)==before.st_size and (before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
             (after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'state_changed_during_read')
        return b
    finally:os.close(fd)

def exclusive(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        view=memoryview(raw)
        while view:
            n=os.write(fd,view);need(n>0,'short_state_write');view=view[n:]
        os.fsync(fd)
    finally:os.close(fd)

class FileStore:
    """Owner argument permits non-root disposable fixtures; live gate requires0."""
    def __init__(self,root,owner=None):
        self.root=Path(root);self.owner=os.getuid() if owner is None else owner;self.healthy=True
        st=self.root.lstat();need(stat.S_ISDIR(st.st_mode) and st.st_uid==self.owner
                                 and st.st_mode&0o077==0,'private_state_root_required')
        self.lock_fd=None;self.phase_fds={};self.bound_session=None
    def lock(self):
        fd=os.open(self.root/'control.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            st=os.fstat(fd);need(stat.S_ISREG(st.st_mode) and st.st_uid==self.owner and st.st_nlink==1
                                and st.st_mode&0o077==0,'unsafe_control_lock')
        except BaseException:os.close(fd);raise
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:os.close(fd);raise Busy('another_operator_or_worker_active')
        self.lock_fd=fd;return self
    def __enter__(self):return self.lock()
    def __exit__(self,*_):
        fcntl.flock(self.lock_fd,fcntl.LOCK_UN);os.close(self.lock_fd);self.lock_fd=None
    def _locked(self):need(self.lock_fd is not None,'exclusive_control_lock_required')
    def active_session(self):
        d=parse(bounded_read(self.root/'active.json',4096));names(d.get('session'));return d['session']
    def session(self):return self.bound_session or self.active_session()
    def bind(self,session):
        need(self.active_session()==session,'active_generation_changed');self.bound_session=session
    def directory(self):return self.root/self.session()
    def create(self,plan):
        self._locked();names(plan['session'])
        # A prior active marker is deliberately retained and blocks rearming.
        need(not (self.root/'active.json').exists() and not (self.root/'active.json').is_symlink(),'active_or_stale_registry_requires_review')
        used=self.root/'used-approvals'
        try:os.mkdir(used,0o700)
        except FileExistsError:
            st=used.lstat();need(stat.S_ISDIR(st.st_mode) and st.st_uid==self.owner and st.st_mode&0o077==0,'unsafe_approval_registry')
        try:exclusive(used/plan['approval_sha256'],canonical({'session':plan['session']}))
        except FileExistsError:raise Refusal('approval_already_consumed')
        exclusive(self.root/'active.json',canonical({'session':plan['session']}))
        self.bound_session=plan['session']
        d=self.root/plan['session'];os.mkdir(d,0o700)
        exclusive(d/'plan.json',canonical(plan));exclusive(d/'events.ndjson',b'')
        exclusive(d/'plan.sha256',sha(canonical(plan)).encode()+b'\n')
        self.event('PREPARING',{})
    def plan(self):
        d=self.directory();raw=bounded_read(d/'plan.json');expected=bounded_read(d/'plan.sha256',128).strip().decode()
        need(sha(raw)==expected,'immutable_plan_changed');p=parse(raw);need(p['session']==self.session(),'registry_binding');return p
    def records(self):
        raw=bounded_read(self.directory()/'events.ndjson');records=[];previous=None
        for i,line in enumerate(raw.splitlines()):
            row=parse(line);need(set(row)=={'sequence','previous_sha256','kind','data','sha256'},'journal_schema')
            expected=row.pop('sha256');need(row['sequence']==i and row['previous_sha256']==previous
                                          and sha(canonical(row))==expected,'journal_tampered_or_partial')
            row['sha256']=expected;previous=expected;records.append(row)
        return records
    def phase(self):
        records=self.records()
        if any(r['kind']=='CLOSED' for r in records):return 'CLOSED'
        return next((r['kind'] for r in reversed(records) if r['kind'] in CONTROL),'PREPARING')
    def event(self,kind,data):
        # Independent workers never acquire the operator lock across CLI calls.
        lock=os.open(self.directory()/'events.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Busy('journal_transaction_busy')
            records=self.records()
            row={'sequence':len(records),'previous_sha256':records[-1]['sha256'] if records else None,'kind':kind,'data':data}
            row['sha256']=sha(canonical(row));raw=canonical(row)+b'\n'
            fd=os.open(self.directory()/'events.ndjson',os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:need(os.write(fd,raw)==len(raw),'partial_journal_write');os.fsync(fd)
            finally:os.close(fd)
            if kind=='ARMED':exclusive(self.directory()/'armed.marker',sha(canonical(self.plan())).encode())
        finally:os.close(lock)
    def is_armed(self):
        try:return bounded_read(self.directory()/'armed.marker',128).decode()==sha(canonical(self.plan()))
        except FileNotFoundError:return False
    def best_effort(self,kind,data):
        try:self.event(kind,data)
        except (OSError,Refusal):self.healthy=False
    def claim(self,phase):
        need(phase in ('grace','deadline'),'phase')
        if self.phase() in ('CLOSED','CLOSING'):return False
        if (self.directory()/(phase+'.complete')).exists():return False
        fd=os.open(self.directory()/(phase+'.lock'),os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Busy('phase_worker_busy')
            if (self.directory()/(phase+'.complete')).exists():os.close(fd);return False
            if self.phase() in ('CLOSED','CLOSING'):os.close(fd);return False
            for number in (1,2):
                try:exclusive(self.directory()/(phase+'.attempt.'+str(number)),canonical({'phase':phase,'attempt':number}));break
                except FileExistsError:continue
            else:raise Refusal('bounded_action_attempts_exhausted')
        except BaseException:os.close(fd);raise
        self.phase_fds[phase]=fd;return True
    def release(self,phase,terminal):
        fd=self.phase_fds.pop(phase)
        try:
            if terminal:
                try:exclusive(self.directory()/(phase+'.complete'),canonical({'phase':phase,'terminal':True}))
                except FileExistsError:pass
        finally:os.close(fd)
    def retire(self):
        self._locked();need(self.phase()=='CLOSED','closed_before_retire')
        # Rename preserves exact pointer bytes as session evidence. No deletion.
        target=self.directory()/'retired-active.json'
        need(not target.exists(),'retired_pointer_collision')
        os.rename(self.root/'active.json',target)
        for directory in (target.parent,self.root):
            fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
        self.bound_session=None
    def assert_workers_idle(self):
        for phase in ('grace','deadline'):
            fd=os.open(self.directory()/(phase+'.lock'),os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            try:
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:raise Busy('worker_still_in_flight')
            finally:os.close(fd)
