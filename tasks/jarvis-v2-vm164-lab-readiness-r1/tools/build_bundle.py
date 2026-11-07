"""Deterministic package from verified RC1, exact wheels, and reviewed dormant serial source."""
from pathlib import Path
import base64,csv,gzip,hashlib,io,json,os,sys,tarfile,uuid,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lab_package import digest,encoded,verify_tar,wheel_payload,load_bundle
P=Path(__file__).resolve().parents[1];MAIN=P.parents[1];RC=MAIN/'tasks/jarvis-v2-unified-rc1';PRE=MAIN/'tasks/jarvis-v2-release-readiness-r1';STORE=Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1');BROKER=MAIN/'tasks/proxmox-automation-phase3-review-r1'
def archive(files):
 out=io.BytesIO()
 with gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0,compresslevel=9) as gz:
  with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as t:
   for n,b in sorted(files.items()):
    m=tarfile.TarInfo(n);m.size=len(b);m.uid=m.gid=m.mtime=0;m.mode=0o644;m.uname=m.gname='';t.addfile(m,io.BytesIO(b))
 return out.getvalue()
def main():
 build=json.loads((RC/'release/BUILD.json').read_text());raw=(RC/build['archive']).read_bytes();assert digest(raw)==build['archive_sha256']
 release=verify_tar(raw);files={}
 for n,h in build['source_sha256'].items():assert digest(release[n])==h;files['source/'+n]=release[n]
 plan=json.loads((MAIN/'tasks/jarvis-authority-readiness-r1/DEPENDENCY-PLAN.json').read_text());selected=plan['selected']
 optional={a['filename']:a for a in json.loads((PRE/'OPTIONAL-DEPENDENCIES.json').read_text())['artifacts']}
 provenance=[];components=[]
 for name,d in sorted(build['dependencies'].items()):
  if name in selected:
   item=selected[name];path=STORE/item['relative_path'];claim=item['record_provenance'];url=item['official_source_url']
  else:
   item=next(a for a in optional.values() if a['filename'].lower().replace('_','-').startswith(name.replace('_','-')+'-'));path=STORE/'artifacts/wheels'/item['filename'];claim='retained official artifact SHA256 + wheel RECORD; publisher attestation not claimed';url=item['url']
  raw=path.read_bytes();assert digest(raw)==d['wheel_sha256'];payload=wheel_payload(raw,name,d['version']);filename=path.name
  files['wheels/'+filename]=raw
  from email.parser import BytesParser
  metadata=BytesParser().parsebytes(next(v for n,v in payload.items() if n.endswith('.dist-info/METADATA')))
  provenance.append({'name':name,'version':d['version'],'filename':filename,'sha256':digest(raw),'artifact_bytes':len(raw),'record_entries':len(payload),'unpacked_bytes':sum(map(len,payload.values())),'requires_dist':metadata.get_all('Requires-Dist',[]),'license_expression':metadata.get('License-Expression'),'retained_upstream_url':url,'provenance_scope':claim})
  components.append({'type':'library','bom-ref':'pkg:pypi/'+name+'@'+d['version'],'name':name,'version':d['version'],'purl':'pkg:pypi/'+name+'@'+d['version'],'hashes':[{'alg':'SHA-256','content':digest(raw)}],'properties':[{'name':'jarvis:scope','value':'installed offline Python closure'},{'name':'jarvis:provenance','value':claim}]})
 # Verify every retained broker packet member and source, using its own sealed inventory.
 verified=0
 for line in (BROKER/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);n=n.removeprefix('./');assert not (BROKER/n).is_symlink() and digest((BROKER/n).read_bytes())==h,n;verified+=1
 for directory in ['src','deploy','tests']:
  for f in sorted((BROKER/directory).rglob('*')):
   if f.is_file():files['serial-candidate/'+str(f.relative_to(BROKER))]=f.read_bytes()
 broker_release=json.loads((BROKER/'RELEASE.json').read_text());files['serial-candidate/RELEASE.json']=(BROKER/'RELEASE.json').read_bytes()
 for name in ['lab_package.py','smoke_runner.py','worker_preflight.py']:files['tools/'+name]=(P/'tools'/name).read_bytes()
 inputs={'child.py':RC/'full_app_child.py','guard.py':MAIN/'tasks/jarvis-fixture-integration-r1/integration_child.py','integration_application.py':RC/'integration_application.py','enrollment_application.py':RC/'enrollment_application.py','recovery_application.py':RC/'recovery_application.py','baseline_api.py':RC/'before/app/agent/api.py','ancestor_hypothesis.py':RC/'ancestor_hypothesis.py'}
 for name,f in inputs.items():files['tools/smoke-inputs/'+name]=f.read_bytes()
 original=files['tools/smoke-inputs/child.py'].decode()
 changed=original.replace("    sys.path.insert(0,'/deps')\n    import yaml","    sys.path.insert(0,'/deps')\n    import runpy\n    runpy.run_path('/input/dependency_check.py',run_name='__main__')\n    import yaml")
 assert changed!=original
 files['tools/smoke-inputs/child.py']=changed.encode()
 files['tools/smoke-inputs/dependency_check.py']=(P/'tools/dependency_check.py').read_bytes()
 os_requirements={'os':'Ubuntu Server 26.04.1 amd64 (VERSION_ID26.04)','python':'CPython3.14.4','sqlite':'3.46.1 exact tested; installed origin must be qualified','openssl':'3.5.5 tested; installed artifact/advisory qualification separate','architecture':'x86_64','minimum_cpu':4,'minimum_RAM_GiB':5,'minimum_free_RAM_GiB':3,'minimum_free_disk_GiB':20,'private_ext4_disk_GiB':64,'no_NIC':True,'bwrap_required_for_smoke':True,'native_runtime_installer_included':False,'OS_packages_to_install_automatically':[],'qualification':'Native OS/runtime artifacts are not this wheel bundle; exact root-protected interpreter hash, filesystem identity and guest boot are operator-bound prerequisites.'}
 files['RUNTIME-PREREQUISITES.json']=encoded(os_requirements)
 (P/'WHEEL-PROVENANCE.json').write_bytes(encoded(provenance))
 lock=json.loads(release['frontend/electron/package-lock.json']);npm=[]
 for path,d in sorted(lock.get('packages',{}).items()):
  if not path or 'node_modules/' not in path or 'version' not in d:continue
  name=d.get('name',path.rsplit('node_modules/',1)[1]);purl='pkg:npm/'+name.replace('@','%40')+'@'+d['version']
  npm.append({'type':'library','bom-ref':purl,'name':name,'version':d['version'],'purl':purl,'scope':'optional','properties':[{'name':'jarvis:scope','value':'source lock metadata only; no Node/Electron binary installed'}]})
 bom={'bomFormat':'CycloneDX','specVersion':'1.6','serialNumber':'urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,build['archive_sha256'])),'version':1,'metadata':{'component':{'type':'application','name':'JARVIS V2 Unified RC1','version':build['git_revision'],'bom-ref':'jarvis-rc1'}},'components':components+npm+[{'type':'application','name':'g6k-serial reviewed dormant candidate','version':broker_release['source_manifest_sha256'],'bom-ref':'g6k-serial-dormant','properties':[{'name':'jarvis:scope','value':'dormant source/deploy examples only; not activated or application adapter'}]}],'dependencies':[{'ref':'jarvis-rc1','dependsOn':[c['bom-ref'] for c in components]}]}
 files['SBOM.cdx.json']=encoded(bom);(P/'SBOM.cdx.json').write_bytes(files['SBOM.cdx.json'])
 manifest={'format':'jarvis-vm164-offline-v1','source_git_revision':build['git_revision'],'source_archive_sha256':build['archive_sha256'],'source_sha256':build['source_sha256'],'real_execution_enabled':False,'dependencies':provenance,'broker_source_manifest_sha256':broker_release['source_manifest_sha256'],'files':{n:digest(b) for n,b in sorted(files.items())}}
 files['MANIFEST.json']=encoded(manifest);raw=archive(files);assert raw==archive(files)
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--directory',default='bundle-final');args=parser.parse_args()
 assert args.directory.replace('-','').isalnum()
 product=P/args.directory;product.mkdir(exist_ok=False);name='jarvis-vm164-rc1-offline-'+digest(raw)[:16]+'.tar.gz';target=product/name
 with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 m,installed=load_bundle(target,digest(raw))
 result={'bundle':str(target.relative_to(P)),'bundle_sha256':digest(raw),'bundle_bytes':len(raw),'bundle_members':len(files),'installed_files':len(installed),'installed_bytes':sum(map(len,installed.values())),'installed_manifest_sha256':digest(installed['INSTALL-MANIFEST.json']),'source_git_revision':build['git_revision'],'source_archive_sha256':build['archive_sha256'],'wheel_count':len(provenance),'broker_packet_members_verified':verified,'broker_source_manifest_sha256':broker_release['source_manifest_sha256'],'deterministic_rebuild_identical':True,'native_OS_runtime_bundled':False,'protected_installation_performed':False,'bootstrap_tool_sha256':digest((P/'tools/lab_package.py').read_bytes())}
 (P/'BUNDLE.json').write_bytes(encoded(result));(product/'MANIFEST.json').write_bytes(files['MANIFEST.json']);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
