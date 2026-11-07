"""Run only in parent's isolated PID/network sandbox: one harmless dummy child."""
import json,os,subprocess,sys,time
from pathlib import Path
from app.config import settings
settings.logging.audit_log='/scratch/process-audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
from app import resource_manager as resources
from app.logs.audit import audit
import psutil
cwd=Path('/scratch/unrelated-service');cwd.mkdir(mode=0o700)
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)','app.main:app'],cwd=cwd,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 proc=psutil.Process(child.pid)
 for _ in range(50):
  try:
   args=proc.cmdline()
   if 'app.main:app' in args:break
  except psutil.NoSuchProcess:raise AssertionError('dummy child exited early')
  time.sleep(0.005)
 actual_cwd=proc.cwd()
 assert Path(actual_cwd)==cwd
 assert not Path(actual_cwd).is_relative_to(resources.PROJECT_ROOT)
 # Safety: permit the genuine helper to consider only this fixture child.
 exclude={p.pid for p in psutil.process_iter() if p.pid!=child.pid}
 selected=resources.discover_jarvis_processes(exclude_pids=exclude)
 before={'child_alive':proc.is_running(),'outside_jarvis_project':not Path(actual_cwd).is_relative_to(resources.PROJECT_ROOT),'same_uid':proc.uids().real==os.getuid(),'classified_role':resources.classify_jarvis_process(proc.name(),' '.join(args),proc),'selected_child':any(p.pid==child.pid for p in selected)}
 stopped=resources.terminate_jarvis_processes(exclude_pids=exclude,timeout=0.5)
 print(json.dumps({'fixture':'single-unrelated-same-uid-sleeping-child','native_selector':'app.main:app','before':before,'stopped_child':any(p['pid']==child.pid and p['outcome']=='terminated' for p in stopped),'child_pid_exists_after':psutil.pid_exists(child.pid),'selected_count':len(selected),'terminated_count':len(stopped)},sort_keys=True))
finally:
 if child.poll() is None:
  child.terminate();child.wait(timeout=1)
 audit._shutdown()
