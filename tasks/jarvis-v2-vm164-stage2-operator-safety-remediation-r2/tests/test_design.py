"""Same assertions applied to original and R2 literal catalogues."""
import unittest
import catalog
CAT=catalog.build()
class Design(unittest.TestCase):
 def test_no_unproved_nss_or_sudo_calls(self):
  for argv in CAT['read'].values():self.assertNotIn(argv[0].rsplit('/',1)[-1],('getent','id','sudo'))
 def test_all_command_budget_categories(self):
  self.assertTrue({'read','manual','install','create','duplicate','show','journal','cgroup','stop'}<=set(CAT.get('operation_caps',{})))
 def test_explicit_environment_contract(self):
  props=CAT.get('service_properties',[])
  for prop in ('SetLoginEnvironment=no','PassEnvironment=','EnvironmentFile=','PAMName=', 'Environment=LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH=/usr/sbin:/usr/bin:/sbin:/bin'):
   self.assertIn(prop,props)
