import copy,sys,unittest
sys.path.insert(0,'/input/tools')
from worker_preflight import assess
GOOD={'source_manifest_matches':True,'source_root_protected':True,'worker_uid_nonroot':True,'worker_gid_matches':True,'worker_login_disabled':True,'tty_owner_matches':True,'tty_mode_private':True,'kernel_serial_console_absent':True,'getty_masked':True,'serial_open_holders':0,'network_interfaces':['lo']}
class Worker(unittest.TestCase):
 def test_metadata_pass_does_not_authorize_activation(self):
  r=assess(GOOD);self.assertTrue(r['metadata_checks_pass']);self.assertFalse(r['activation_ready'])
 def test_unknown_holders_block(self):
  d=dict(GOOD);d['serial_open_holders']=None;self.assertFalse(assess(d)['metadata_checks_pass'])
for key in GOOD:
 def test(self,k=key):
  d=dict(GOOD);d[k]=['lo','eth0'] if k=='network_interfaces' else 1 if k=='serial_open_holders' else False
  self.assertFalse(assess(d)['metadata_checks_pass'])
 setattr(Worker,'test_refuses_'+key,test)
