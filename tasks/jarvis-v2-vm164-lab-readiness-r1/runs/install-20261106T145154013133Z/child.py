import sys,unittest,json,os
sys.path.insert(0,'/input/tests')
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('/input/tests'))
from pathlib import Path
Path('/work/TEST-RESULTS.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),'successful':result.wasSuccessful(),'uid':os.getuid(),'guest_or_protected_install_performed':False},indent=2)+'\n')
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
