"""Deterministic same-UID path-switch mechanics only; never proof of another UID."""
from pathlib import Path
import sqlite3,os,json,uuid
from app.agent.ledger import LedgerGuard,digest_state
from app.agent.authority import AuthorityError,Actor,canonical
from synthetic_authority import fixture_authority,seed_legacy_fixture
root=Path('/scratch/ancestor-mechanics');root.mkdir(mode=0o700)
key=b'synthetic-audit-ledger-key-only-000000000000';store=str(uuid.uuid4());actor=Actor('local-service')
base=root/'slot';db=base/'state.sqlite';anchors=root/'anchors'
g=LedgerGuard(anchors,key,store,initialize=True)
a=fixture_authority(db,ledger=g);a.submit(actor,str(uuid.uuid4()),'original victim task');a.close()
shadow=root/'shadow';fake=shadow/'state.sqlite';seed_legacy_fixture(fake)
request_id=str(uuid.uuid4());c=sqlite3.connect(fake)
c.execute('INSERT INTO records VALUES(?,?,?,?)',('task',request_id,actor.scope,canonical({'task_id':request_id,'scope':actor.scope,'goal':'injected synthetic task','status':'pending'})))
c.commit();c.close()
original_connect=sqlite3.connect;swapped=False
saved=root/'saved';moved=root/'moved'
def connect(path,*args,**kwargs):
 global swapped
 if not swapped and isinstance(path,Path) and path==db:
  swapped=True
  base.rename(saved);shadow.rename(base)
  conn=original_connect(path,*args,**kwargs)
  # Restore expected pathname identity before Authority's subsequent fences.
  base.rename(moved);saved.rename(base)
  return conn
 return original_connect(path,*args,**kwargs)
sqlite3.connect=connect
try:
 g2=LedgerGuard(anchors,key,store)
 try:
  a2=fixture_authority(db,ledger=g2)
 except Exception as exc:
  print(json.dumps({'same_uid_mechanics_only':True,'swapped':swapped,'constructor_result':type(exc).__name__,'error':str(exc)}))
 else:
  try:
   out={'same_uid_mechanics_only':True,'swapped':swapped,'constructor_result':'accepted','connected_digest':digest_state(a2._conn)['sha256'],'injected_task':a2.get_task(actor,request_id)}
   out['ready']=a2.readiness()
   print(json.dumps(out,sort_keys=True))
  except Exception as exc:print(json.dumps({'same_uid_mechanics_only':True,'swapped':swapped,'constructor_result':'accepted','subsequent_error':type(exc).__name__,'error':str(exc)}))
  finally:a2.close()
finally:sqlite3.connect=original_connect
