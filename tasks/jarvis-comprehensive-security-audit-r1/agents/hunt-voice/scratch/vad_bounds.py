"""Parent OS-sandbox only: finite fake capture, no audio/hardware/native package."""
import io,json,sys,types,wave
from app.config import settings
settings.logging.audit_log='/scratch/vad-audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
from app.voice import vad as module
from app.logs.audit import audit
frame=b'\x01\x00'*480
queued_frames=42
class FakeStream:
    def __init__(self,**kwargs): self.callback=kwargs['callback']
    def __enter__(self):
        for i in range(queued_frames):
            self.callback(frame if i<41 else b'\x00'*len(frame),480,None,None)
        return self
    def __exit__(self,*args): return False
class FakeVad:
    def __init__(self,*args): pass
    def is_speech(self,data,sample_rate): return data[0]==1
sys.modules['sounddevice']=types.SimpleNamespace(RawInputStream=FakeStream)
sys.modules['webrtcvad']=types.SimpleNamespace(Vad=FakeVad)
v=module.VoiceActivityDetector()
v.max_record_seconds=0.6
v.min_speech_seconds=0.03
v.trailing_silence_seconds=0.03
raw=v.record_until_silence()
with wave.open(io.BytesIO(raw),'rb') as w:
    actual_frames=w.getnframes()//480
    result={'fixture':'finite-fake-audio-no-hardware','configured_seconds':v.max_record_seconds,'expected_audio_frames_cap':int(v.max_record_seconds*1000/v.frame_ms),'provided_speech_frames':41,'provided_silence_frames':1,'recorded_audio_frames':actual_frames,'recorded_seconds':w.getnframes()/w.getframerate(),'wav_bytes':len(raw)}
assert result['recorded_audio_frames']==42
assert result['recorded_audio_frames']>result['expected_audio_frames_cap']
print(json.dumps(result,sort_keys=True))
audit._shutdown()
