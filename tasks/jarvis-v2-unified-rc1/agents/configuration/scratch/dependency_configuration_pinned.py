"""Offline metadata consistency and audit availability; no installation/network."""
import importlib.metadata as md,json,subprocess,sys,shutil
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version
from app.config import settings,load_settings
installed={canonicalize_name(d.metadata['Name']):d for d in md.distributions(path=['/deps'])}
missing=[];checked=[]
for name,d in sorted(installed.items()):
    for raw in d.requires or []:
        req=Requirement(raw)
        if req.marker and not req.marker.evaluate({'extra':''}):continue
        key=canonicalize_name(req.name)
        checked.append({'distribution':name,'requirement':raw})
        if key not in installed or Version(installed[key].version) not in req.specifier:
            missing.append({'distribution':name,'requirement':raw})
config=load_settings(Path('/target/config.yaml.example'))
assert config.safety.dry_run and not config.resource_mode.enabled
assert not config.resource_mode.auto_light_sleep and not config.resource_mode.auto_deep_sleep
assert not config.voice.dictation_enabled and not config.boot.enabled and not config.openjarvis.trace_logging_enabled
lock=json.loads(Path('/target/frontend/electron/package-lock.json').read_text())
audit=[]
for command in [[sys.executable,'-m','pip_audit','-r','/target/requirements.txt'],[sys.executable,'-m','pip','check']]:
    r=subprocess.run(command,capture_output=True,text=True,timeout=5)
    audit.append({'command':command,'exitcode':r.returncode,'stdout':r.stdout[:4096],'stderr':r.stderr[:4096]})
npm=shutil.which('npm')
if npm:
    command=[npm,'audit','--offline','--package-lock-only','--ignore-scripts','--prefix','/target/frontend/electron','--audit-level=high']
    r=subprocess.run(command,capture_output=True,text=True,timeout=8)
    audit.append({'command':command,'exitcode':r.returncode,'stdout':r.stdout[:4096],'stderr':r.stderr[:4096]})
else:audit.append({'command':['npm','audit','--offline'],'status':'NOT_AVAILABLE_IN_QUALIFIED_CAGE'})
print(json.dumps({'installed_versions':{n:d.version for n,d in sorted(installed.items())},'metadata_requirements_checked':checked,'unsatisfied_metadata_dependencies':missing,'safe_public_configuration_validated':True,'electron_lock_version':lock['lockfileVersion'],'electron_lock_packages':len(lock.get('packages',{})),'audit_attempts':audit,'fresh_advisory_verdict':'NOT_VERIFIED_OFFLINE; live deployment blocker','host_or_target_packages_modified':False},sort_keys=True))
assert not missing,missing
