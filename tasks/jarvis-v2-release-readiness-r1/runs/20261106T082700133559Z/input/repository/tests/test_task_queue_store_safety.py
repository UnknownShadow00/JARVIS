"""Independent legacy stores are refused before reading or writing their bytes."""
from pathlib import Path
import pytest
from app.agent.authority import Authority,AuthorityError
from app.agent.task_queue import TaskQueue
from app.agent.scheduler import Scheduler

@pytest.mark.parametrize('payload',['[]','{malformed','[{"task_id":"old"}]'])
@pytest.mark.parametrize('interface',[TaskQueue,Scheduler])
def test_legacy_store_refused_and_preserved(tmp_path,payload,interface):
    path=tmp_path/'legacy.json';path.write_text(payload)
    with pytest.raises(AuthorityError,match='independent_store_disabled'):interface(path)
    assert path.read_text()==payload and len(list(tmp_path.iterdir()))==1

def test_missing_authority_not_created(tmp_path):
    path=tmp_path/'new/state.sqlite'
    with pytest.raises(AuthorityError,match='authority_unenrolled_or_missing'):Authority(path)
    assert not path.parent.exists()
