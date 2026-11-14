"""Exact pre-creation absence proof. Caller supplies raw captured evidence."""
from common import need,integer
import packet as p
from binding import properties
FIELDS={'Id','Names','LoadState','ActiveState','SubState','Job','FragmentPath','SourcePath','Transient'}
def absent(session,case,proof):
 name=p.unit(session['nonce'],case);p.validate_session(session)
 need(type(proof) is dict and proof.get('boot_id')==session['boot_id'],'collision boot binding')
 p.window(session,proof.get('sample'))
 paths=proof.get('unit_paths');need(type(paths) is list and paths and len(paths)==len(set(paths)),'complete UnitPath inventory')
 need(all(type(x) is str and x.startswith('/') and not any(y in ('','..','.') for y in x.split('/')[1:]) for x in paths),'canonical UnitPath')
 need(proof.get('unit_paths_complete') is True and proof.get('namespace_inventory')==[],'namespace occupied/incomplete')
 units=[name+'.timer',name+'.service',name+'-absent.service']
 rows=proof.get('units');need(type(rows) is dict and set(rows)==set(units),'three collision targets')
 for unit in units:
  row=rows[unit];s=properties(row.get('raw_show'),FIELDS)
  need(s['Id']==unit and s['Names'] in ('',unit) and s['LoadState']=='not-found' and s['ActiveState']=='inactive' and s['SubState']=='dead' and s['Job']=='0' and s['FragmentPath']==s['SourcePath']=='' and s['Transient']=='no','unit exists or absence ambiguous')
  need(row.get('show_exit') in (0,1) and type(row.get('show_exit')) is int,'unknown show exit')
  files=row.get('files');need(type(files) is dict and set(files)=={path+'/'+unit for path in paths},'incomplete file collision inspection')
  need(all(v=={'absent':True,'errno':'ENOENT'} for v in files.values()),'file/symlink collision or error')
 return True
