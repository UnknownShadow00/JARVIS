"""Confirmed audit mechanics; all effects confined to the networkless cage."""
from types import SimpleNamespace
from unittest.mock import Mock,AsyncMock
import io
import os
from pathlib import Path
import subprocess
import sys
import wave
import pytest
from fastapi.testclient import TestClient
from app.server import app,manager
from app.config import settings
import app.resource_manager as resources
import app.cli as cli
from app.voice.vad import VoiceActivityDetector
from app.voice.dictation import Dictation


@pytest.mark.parametrize('path',['/resource/sleep/light','/resource/sleep/deep','/resource/wake','/resource/shutdown'])
def test_effectful_resource_http_is_inert_even_with_bearer(monkeypatch,path):
    monkeypatch.setattr(settings.server,'api_token','synthetic-control-key')
    for method in ('light_sleep','deep_sleep','wake'):
        monkeypatch.setattr(resources.resource_manager,method,AsyncMock(side_effect=AssertionError('host control forbidden')))
    response=TestClient(app).post(path,headers={'Authorization':'Bearer synthetic-control-key'})
    assert response.status_code==403 and response.json()['error']=='offline_operator_control_required'


def test_stop_requires_configured_identity(monkeypatch):
    monkeypatch.setattr(settings.server,'api_token','')
    assert TestClient(app).post('/stop').status_code==401


@pytest.mark.parametrize('value',[[],{'message':4},{'message':{}},{'message':'x'*9000}])
def test_malformed_websocket_closes_and_removes_manager_entry(monkeypatch,value):
    from starlette.websockets import WebSocketDisconnect
    monkeypatch.setattr(settings.server,'api_token','synthetic-ws-key')
    original=len(manager.active)
    with TestClient(app).websocket_connect('/ws',headers={'Authorization':'Bearer synthetic-ws-key'}) as channel:
        channel.send_json(value)
        with pytest.raises(WebSocketDisconnect):channel.receive_json()
    assert len(manager.active)==original


@pytest.mark.parametrize('status',[401,403,500])
def test_cli_post_auth_and_status_failure_never_falls_back(monkeypatch,status):
    import httpx
    captured={}
    monkeypatch.setattr(settings.server,'api_token','synthetic-cli-key')
    def denied(url,**kwargs):
        captured.update(kwargs)
        return httpx.Response(status,request=httpx.Request('POST',url),json={'error':'synthetic refusal'})
    monkeypatch.setattr(cli.httpx,'post',denied)
    monkeypatch.setattr(cli,'_local_light_sleep',AsyncMock(side_effect=AssertionError('fallback forbidden')))
    assert cli.main(['sleep','--light','--offline'])==1
    assert captured['headers']=={'Authorization':'Bearer synthetic-cli-key'}


def test_cli_timeout_has_unknown_outcome_and_never_falls_back(monkeypatch):
    import httpx
    monkeypatch.setattr(cli.httpx,'post',Mock(side_effect=httpx.ReadTimeout('synthetic timeout')))
    monkeypatch.setattr(cli,'_local_light_sleep',AsyncMock(side_effect=AssertionError('fallback forbidden')))
    assert cli.main(['sleep','--light','--offline'])==1


def test_cli_unreachable_requires_explicit_offline_control(monkeypatch):
    import httpx
    monkeypatch.setattr(cli.httpx,'post',Mock(side_effect=httpx.ConnectError('synthetic unavailable')))
    monkeypatch.setattr(cli,'_local_light_sleep',AsyncMock(side_effect=AssertionError('implicit local fallback forbidden')))
    assert cli.main(['sleep','--light'])==1


def test_untracked_same_entrypoint_child_is_never_terminated(tmp_path,monkeypatch):
    monkeypatch.setattr(resources,'_owned_processes',{})
    child=subprocess.Popen([sys.executable,'-I','-S','-c','import time; time.sleep(10)','app.main:app'],cwd=tmp_path)
    try:
        assert resources.terminate_jarvis_processes()==[] and child.poll() is None
    finally:child.kill();child.wait(timeout=5)


@pytest.mark.parametrize('stale',[False,True])
def test_only_positive_native_child_lease_allows_signal(tmp_path,monkeypatch,stale):
    real_popen=subprocess.Popen
    monkeypatch.setattr(resources,'_owned_processes',{})
    def dummy(*args,**kwargs):
        return real_popen([sys.executable,'-I','-S','-c','import time; time.sleep(10)'],cwd=resources.PROJECT_ROOT)
    monkeypatch.setattr(resources.subprocess,'Popen',dummy)
    child=resources.start_server_process()
    try:
        assert child.pid in resources._owned_processes
        if stale:resources._owned_processes[child.pid]['created_at']-=1
        stopped=resources.terminate_jarvis_processes(timeout=.5)
        if stale:assert stopped==[] and child.poll() is None
        else:assert stopped[0]['pid']==child.pid and child.poll() is not None
    finally:
        if child.poll() is None:child.kill();child.wait(timeout=5)


def test_vad_continuous_speech_respects_frame_and_callback_queue_bounds():
    v=VoiceActivityDetector();v.min_speech_seconds=.03
    frame=b'\x00'*(v.sample_rate*v.frame_ms//1000*2)
    class Input:
        def __init__(self,**kwargs):self.callback=kwargs['callback']
        def __enter__(self):
            for _ in range(200):self.callback(frame,0,None,None)
        def __exit__(self,*args):pass
    wav=v._record_from_stream(Input,SimpleNamespace(is_speech=lambda *args:True),timeout=.6,cancelled=lambda:False)
    with wave.open(io.BytesIO(wav),'rb') as stream:assert stream.getnframes()==v.sample_rate*20*v.frame_ms//1000


def test_vad_active_capture_cancellation_is_checked_each_frame():
    v=VoiceActivityDetector();v.min_speech_seconds=.03;calls=[0]
    frame=b'\x00'*(v.sample_rate*v.frame_ms//1000*2)
    class Input:
        def __init__(self,**kwargs):self.callback=kwargs['callback']
        def __enter__(self):
            for _ in range(50):self.callback(frame,0,None,None)
        def __exit__(self,*args):pass
    def speech(*args):calls[0]+=1;return True
    wav=v._record_from_stream(Input,SimpleNamespace(is_speech=speech),timeout=1,cancelled=lambda:calls[0]>=3)
    with wave.open(io.BytesIO(wav),'rb') as stream:assert stream.getnframes()==v.sample_rate*3*v.frame_ms//1000


def test_dictation_never_touches_desktop_or_logs_transcript(monkeypatch):
    from app.voice import dictation as module
    events=[];copy=Mock(side_effect=AssertionError('clipboard forbidden'));type_out=Mock(side_effect=AssertionError('typing forbidden'))
    monkeypatch.setattr(module,'pyperclip',SimpleNamespace(copy=copy));monkeypatch.setattr(module,'pyautogui',SimpleNamespace(write=type_out))
    monkeypatch.setattr(module.audit,'log',lambda event,data:events.append((event,data)))
    assert Dictation().handle_transcript('synthetic private transcript') is False
    copy.assert_not_called();type_out.assert_not_called();assert 'synthetic private transcript' not in repr(events)


@pytest.mark.parametrize('args',[['wake','--offline'],['sleep','--deep','--offline'],['shutdown','--offline']])
def test_no_server_or_offline_flag_can_start_or_mutate_local_resources(monkeypatch,args):
    import httpx
    monkeypatch.setattr(cli.httpx,'post',Mock(side_effect=httpx.ConnectError('synthetic unavailable')))
    for method in ('wake','light_sleep','deep_sleep'):
        monkeypatch.setattr(resources.resource_manager,method,AsyncMock(side_effect=AssertionError('local host control forbidden')))
    for module in (resources,cli):
        monkeypatch.setattr(module,'start_server_process',Mock(side_effect=AssertionError('implicit server start forbidden')),raising=False)
        monkeypatch.setattr(module,'terminate_jarvis_processes',Mock(side_effect=AssertionError('implicit process stop forbidden')),raising=False)
    assert cli.main(args)==1
