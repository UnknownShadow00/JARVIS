"""Fixture-backed host; no subprocess, network, systemd or real VM interface."""
import copy
import datetime as dt
from model import *
from store import MemoryStore

class FakeClock:
    def __init__(self,us=1_000_000_000,boot_id='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'):
        self.value=us;self.boot_id=boot_id;self.wall=stamp('2026-11-06T21:00:00Z')
    def us(self):return self.value
    def utc(self):return self.wall
    def advance(self,us):self.value+=us

def config():
    return {'name':'jarvis-g6k-clean-164','smbios1':'uuid='+UUID,'scsi0':DISK+',serial='+SERIAL+',size=64G',
            'ide2':ISO+',media=cdrom','boot':'order=scsi0','hotplug':'0','agent':'0','onboot':'0','protection':'1',
            'serial0':'socket','vga':'std','bios':'seabios','machine':'q35','digest':'a'*40,
            'cores':4,'sockets':1,'memory':6000,'balloon':0}

def approval(clock,source_hash,policy='A'):
    return {'format':'vm164-r3-reviewed-authorization','kind':'synthetic','policy':policy,'stage':3,
            'purpose':'non_root_vm164_qualification','operator_reference':'SYNTHETIC-ONLY',
            'review_sha256':'b'*64,'source_sha256':source_hash,'host_boot_id':clock.boot_id,
            'issued_at':'2026-11-06T20:59:00Z','expires_at':'2026-11-06T21:45:00Z',
            'stage2_record_sha256':'c'*64,'command_contract_reviewed':True,
            'forced_stop_authorization':None if policy=='A' else {'policy':'B','vmid':164,
                'review_sha256':'d'*64,'accepts_disk_loss':True,'explicit_forced_termination':True}}

class FixtureBackend:
    simulated=True
    def __init__(self,clock,cfg=None):
        self.clock=clock;self.cfg=copy.deepcopy(cfg or config());self.status='stopped';self.pending=[]
        self.actions=[];self.units={};self.fail={};self.overrides={};self.grace_stops=True
        self.force_grant=None;self.canary_ok=True;self.collisions=set();self.stop_callback=None
    def _hit(self,op):
        self.actions.append((op,164))
        if op in self.fail:raise self.fail[op]
    def snapshot(self):
        self._hit('snapshot');d={'node':'pve','vmid':164,'host_boot_id':self.clock.boot_id,
            'began_us':self.clock.us(),'ended_us':self.clock.us(),'config':copy.deepcopy(self.cfg),
            'status':{'vmid':164,'status':self.status},'pending':copy.deepcopy(self.pending),
            'iso':{'volume':ISO,'sha256':ISO_SHA,'bytes':196608,'config_digest':self.cfg['digest']}}
        d.update(copy.deepcopy(self.overrides));return d
    def unit_exists(self,n):
        self._hit('unit_exists')
        return n in self.collisions or any(n==d[k]['id'] for d in self.units.values() for k in ('timer','service'))
    def canary(self,plan):self._hit('canary');return self.canary_ok
    def create_timer(self,plan,phase):
        self._hit('create_'+phase)
        self.units[phase]={'timer':{'id':plan['names'][phase]+'.timer','transient':True,'load':'loaded',
            'active':'active','sub':'waiting','result':'success','trigger':plan['names'][phase]+'.service',
            'wake':True,'accuracy_us':1,'random_us':0,'last_trigger_us':0,'remain':True,
            'on_boot_us':plan[phase+'_us'],'next_us':plan[phase+'_us'],
            'next_boot_min_us':plan[phase+'_us'],'next_boot_max_us':plan[phase+'_us'],
            'readback_clock':'CLOCK_BOOTTIME','readback_offset_low_us':0,'readback_offset_high_us':0},
            'service':{'id':plan['names'][phase]+'.service','transient':True,'load':'loaded','active':'inactive',
            'sub':'dead','result':'success','type':'exec','argv':worker_argv(plan['session'],phase),
            'user':'root','group':'root','restart':'no','kill_mode':'control-group',
            'runtime_us':45_000_000 if phase=='grace' else 30_000_000,
            'stop_timeout_us':5_000_000,'extra_commands':False,'umask':'0077','memory_max':'134217728',
            'tasks_max':'16','send_sigkill':True,'stdin':'null','stdout':'journal','stderr':'journal',
            'start_timeout_us':10_000_000}}
    def unit_proof(self,plan,phase):
        self._hit('proof_'+phase);return {'host_boot_id':self.clock.boot_id,'observed_us':self.clock.us(),**copy.deepcopy(self.units[phase])}
    def start_vm(self):self._hit('start');self.status='running'
    def graceful(self):
        self._hit('graceful')
        if self.grace_stops:self.status='stopped'
    def force(self,grant=None):
        need(grant is not None and grant==self.force_grant,'unauthorized_fixture_force')
        self._hit('force_SIMULATED_ONLY');self.status='stopped'
    def stop_own_units(self,plan,phase):
        self._hit('cancel_'+phase)
        if self.stop_callback:self.stop_callback(phase)
        for k in ('timer','service'):self.units[phase][k]['active']='inactive';self.units[phase][k]['sub']='dead'
    def units_inactive(self,plan,phase):return all(self.units[phase][k]['active']=='inactive' for k in ('timer','service'))
