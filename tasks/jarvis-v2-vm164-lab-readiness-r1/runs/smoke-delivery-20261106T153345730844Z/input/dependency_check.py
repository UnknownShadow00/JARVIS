"""Run only inside the smoke cage after boundary verification; pure metadata + native probes."""
import importlib.metadata as md,json,os,sqlite3,ssl,sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version
installed={canonicalize_name(d.metadata['Name']):d for d in md.distributions(path=['/deps'])}
assert len(installed)==31
checked=[]
for name,d in sorted(installed.items()):
 for raw in d.requires or []:
  req=Requirement(raw)
  if req.marker and not req.marker.evaluate({'extra':''}):continue
  key=canonicalize_name(req.name);assert key in installed and Version(installed[key].version) in req.specifier,(name,raw)
  checked.append({'distribution':name,'requirement':raw})
assert sqlite3.sqlite_version=='3.46.1'
assert ssl.OPENSSL_VERSION=='OpenSSL 3.5.5 27 Jan 2026'
import numpy,bs4
assert int(numpy.array([1,2,3]).sum())==6
assert bs4.BeautifulSoup('<b>synthetic</b>','html.parser').b.text=='synthetic'
result={'status':'PASS','distributions':{n:d.version for n,d in sorted(installed.items())},'active_metadata_edges_checked':checked,'native_numpy_and_bs4_execution':True,'sqlite':sqlite3.sqlite_version,'openssl':ssl.OPENSSL_VERSION,'OSV_advisory_pass_claimed':False}
Path('/work/DEPENDENCY-CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
