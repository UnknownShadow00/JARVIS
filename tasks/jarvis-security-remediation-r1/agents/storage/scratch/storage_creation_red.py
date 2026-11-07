import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
import pytest
raise SystemExit(pytest.main(['-q','--tb=short','-p','no:cacheprovider','--basetemp=/scratch/pytest','/input/helpers/test_storage_ancestry_security.py','-k','unsafe_ancestor_refused_before_creating_descendants']))
