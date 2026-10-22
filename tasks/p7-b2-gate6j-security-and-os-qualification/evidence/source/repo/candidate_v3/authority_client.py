"""Service capability adapter for the existing Runtime and CheckpointWriter.
Contains no signing method, protected path, protected DB handle or operator client.
"""
from dataclasses import asdict
from .contracts import Refused,canonical,digest
from .runtime_authority import token,projection,accepted_rows

class ServiceAuthorityClient:
    def __init__(self,connection,*,contracts):
        self.connection=connection;self.contracts=dict(contracts)
        self.cursor=None

    def read(self):
        s=self.connection.call('READ',{});self.cursor=token(s);return s

    def _call(self,operation,**args):
        if self.cursor is None:self.read()
        result=self.connection.call(operation,dict(expected=self.cursor,**args))
        self.cursor=result;return result

    def check(self,store,*,allow_terminal=False):
        s=self.read()
        if accepted_rows(store.db)!=s['accepted']:raise Refused('PROTECTED_ACCEPTANCE_MISMATCH')
        self._call('CHECK',allow_terminal=allow_terminal)
        return s

    def command(self,nonce):
        if type(nonce) is not str or len(nonce)!=32 or any(c not in '0123456789abcdef' for c in nonce):raise Refused('PROTECTED_COMMAND_IDENTIFIER')
        s=self.read();a=s['commands'].get(nonce)
        if a is None:raise Refused('PROTECTED_OPERATOR_APPROVAL_REQUIRED')
        return a

    def approved(self,a):
        s=self.read()
        if s['commands'].get(a['nonce'])!=a:raise Refused('PROTECTED_OPERATOR_APPROVAL_REQUIRED')
        self._call('CLAIM',nonce=a['nonce'])

    def before_accept(self,store,transport,session,commitment):
        self.check(store)
        p=store.db.execute('SELECT nonce,transport,session,commitment FROM permits WHERE spent=0').fetchone()
        if p is None or p[1:]!=(transport,session,commitment):raise Refused('PROTECTED_PERMIT_ASSOCIATION')
        self._call('CONSUME',permit=p[0])

    def after_accept(self,store):
        self._call('BIND');self.check(store)

    def possible_send(self,store,aid,kind,contract,request_digest):
        self.check(store)
        roles=[r for r,c in self.contracts.items() if c==contract]
        if len(roles)!=1:raise Refused('PROTECTED_RESOURCE_BINDING')
        role=roles[0]
        expected='GRANITE' if role=='granite' else 'LEGACY_ROUTER' if role=='legacy_router' else 'LEGACY_RESPONDER'
        if kind!=expected:raise Refused('PROTECTED_SUBSTEP_BINDING')
        row=store.db.execute('SELECT ordinal FROM attempts WHERE id=?',(aid,)).fetchone()
        if row is None:raise Refused('PROTECTED_ATTEMPT_BINDING')
        self._call('SEND',ordinal=row[0],role=role,request_digest=request_digest)

    def dispatch_once(self,request):
        roles=[role for role,c in self.contracts.items() if c.resource==request.resource]
        if len(roles)!=1 or digest(request.body)!=request.request_digest:raise Refused('PROTECTED_DISPATCH_RESOURCE')
        self.read()
        self._call('DISPATCH',attempt=request.attempt,substep=request.substep,role=roles[0],request_digest=request.request_digest)

    def settle(self):self._call('SETTLE')

    def export_db(self):
        s=self.read()
        return projection(s),token(s)

    def checkpoint_committed(self,bundle):self._call('CHECKPOINT',bundle=bundle.name)

    def terminal(self,store):
        # Emergency local closure does not depend on helper availability.
        try:
            self.cursor=self.connection.call('TERMINATE',{})
            if self.read()['terminal_status']!=store.terminal():store.stop('FINAL_CHECKPOINT_FAILED')
        except Refused:
            store.stop('FINAL_CHECKPOINT_FAILED')  # never present an unverified protected stop as complete
