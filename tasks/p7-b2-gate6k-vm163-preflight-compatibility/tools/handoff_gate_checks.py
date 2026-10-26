"""Mocked root-CLI dispatch policy only; no privilege, extraction or VM execution."""
import sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,'/home/nexus/.local/share/jarvis-gate6k-preflight-fix/candidate-r1/disposable')
import safe_extract

class HandoffGateTests(unittest.TestCase):
    def call(self,*,destination='/opt/g6k-preflight-r1',hostname='jarvis-security',interfaces=('lo',),allowed=False):
        args=['safe_extract.py','/synthetic/archive','a'*64,'b'*64,'--destination',destination]
        with patch.object(sys,'argv',args),patch.object(safe_extract.os,'geteuid',return_value=0),patch.object(safe_extract.os,'uname',return_value=SimpleNamespace(nodename=hostname)),patch.object(Path,'iterdir',return_value=[SimpleNamespace(name=n) for n in interfaces]),patch.object(safe_extract,'extract',return_value={'result':'MOCK_ONLY'}) as extract,patch('builtins.print'):
            if allowed:
                safe_extract.main();extract.assert_called_once_with('/synthetic/archive',destination,'a'*64,'b'*64)
            else:
                with self.assertRaisesRegex(ValueError,'ROOT_EXTRACTION_TARGET_REFUSED'):safe_extract.main()
                extract.assert_not_called()
    def test_new_exact_destination_dispatches_only_mock(self):self.call(allowed=True)
    def test_old_installed_release_cannot_be_replaced(self):self.call(destination='/opt/g6j-release')
    def test_other_destination_refuses(self):self.call(destination='/opt/other')
    def test_nexus_still_refuses(self):self.call(hostname='nexus-services')
    def test_external_interface_still_refuses(self):self.call(interfaces=('lo','ens18'))

if __name__=='__main__':unittest.main(verbosity=2)
