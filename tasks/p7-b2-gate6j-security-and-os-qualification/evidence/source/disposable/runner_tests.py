"""Unprivileged package qualification. Does NOT run main/provisioning or change UID."""
import json,multiprocessing,os,subprocess,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from process_boundary import role_context,SafePipe
from qualify_multi_uid import validate_roles,mutation_denials,ROLES
from qualify_all import run_suite,suite_command,seal_reports
from safety_preflight import validate_environment,validate_approval,verify_manifest


def probe(pipe,fd,identity):
    try:
        st=os.fstat(fd);inherited=(st.st_dev,st.st_ino)==identity
    except OSError:inherited=False
    pipe.send(inherited);pipe.close()

def safe_child(pipe):
    pipe.send({'uid':os.getuid(),'pid':os.getpid()});pipe.close()

class RunnerTests(unittest.TestCase):
    def probe_context(self,context):
        with tempfile.TemporaryFile() as canary:
            os.set_inheritable(canary.fileno(),True);st=os.fstat(canary.fileno())
            parent,other=context.Pipe();child=context.Process(target=probe,args=(other,canary.fileno(),(st.st_dev,st.st_ino)))
            child.start();other.close()
            try:
                self.assertTrue(parent.poll(10));result=parent.recv();child.join(10);self.assertEqual(child.exitcode,0);return result
            finally:
                parent.close()
                if child.is_alive():child.terminate();child.join()
    def test_fork_negative_control_inherits_operator_channel(self):
        self.assertTrue(self.probe_context(multiprocessing.get_context('fork')))
    def test_spawn_excludes_unrelated_parent_descriptor(self):
        self.assertFalse(self.probe_context(role_context()))
    def entries(self):return {r:NS(pw_uid=1001+i,pw_gid=1001+i,pw_shell='/usr/sbin/nologin') for i,r in enumerate(ROLES)}
    def test_private_roles(self):validate_roles(self.entries(),[])
    def test_shared_group_refused(self):
        entries=self.entries();entries[ROLES[1]].pw_gid=entries[ROLES[0]].pw_gid
        with self.assertRaises(RuntimeError):validate_roles(entries,[])
    def test_root_uid_refused(self):
        entries=self.entries();entries[ROLES[0]].pw_uid=0
        with self.assertRaises(RuntimeError):validate_roles(entries,[])
    def test_supplementary_group_refused(self):
        with self.assertRaises(RuntimeError):validate_roles(self.entries(),[NS(gr_gid=27,gr_mem=[ROLES[0]])])
    def test_login_role_refused(self):
        entries=self.entries();entries[ROLES[0]].pw_shell='/bin/bash'
        with self.assertRaises(RuntimeError):validate_roles(entries,[])
    def test_mutation_denial_does_not_swallow_missing_path(self):
        with patch('qualify_multi_uid.os.open',side_effect=FileNotFoundError()):
            with self.assertRaises(FileNotFoundError):mutation_denials([Path('/fixture/only')])
    def test_mutation_denial_requires_kernel_permission_error(self):
        from contextlib import ExitStack
        with ExitStack() as stack:
            for name in ('open','chmod','unlink','rename','link','symlink'):
                stack.enter_context(patch('qualify_multi_uid.os.'+name,side_effect=PermissionError()))
            self.assertEqual(mutation_denials([Path('/fixture/only')]),[True]*6)
    def environment(self,**changes):
        value=dict(hostname='throwaway-g6j',interfaces=['lo'],mountinfo='1 0 8:1 / / rw - ext4 /dev/vda1 rw\n2 1 0:1 / /proc rw - proc proc rw',credential_paths=[])
        value.update(changes);validate_environment(**value)
    def test_valid_environment_shape_only(self):self.environment()
    def test_reject_known_targets(self):
        for host in ('jarvis','nexus-services','ai-server','proxmox','pve'):
            with self.subTest(host=host),self.assertRaises(RuntimeError):self.environment(hostname=host)
    def test_reject_network_interface(self):
        with self.assertRaises(RuntimeError):self.environment(interfaces=['lo','eth0'])
    def test_reject_credential_presence_without_reading(self):
        with self.assertRaises(RuntimeError):self.environment(credential_paths=['/root/.ssh'])
    def test_reject_shared_mount(self):
        for filesystem in ('nfs','virtiofs','9p','cifs','ext4'):
            with self.subTest(fs=filesystem),self.assertRaises(RuntimeError):
                self.environment(mountinfo='1 0 8:1 / / rw - ext4 /dev/vda1 rw\n2 1 0:1 / /mnt rw - '+filesystem+' host rw')
    def test_reject_container_root(self):
        with self.assertRaises(RuntimeError):self.environment(mountinfo='1 0 0:1 / / rw - overlay overlay rw')
    def test_reject_marker_without_manifest_and_vm_attestation(self):
        with self.assertRaises(RuntimeError):validate_approval({},'fixture-machine')
    def test_manifest_positive_and_tamper(self):
        import hashlib
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory);source=root/'source';source.write_text('fixture');source.chmod(0o600)
            manifest=root/'SOURCE-SHA256SUMS';manifest.write_text(hashlib.sha256(source.read_bytes()).hexdigest()+'  source\n');manifest.chmod(0o600)
            seal=hashlib.sha256(manifest.read_bytes()).hexdigest()
            self.assertEqual(verify_manifest(root,seal,owner_uid=os.getuid()),1)
            source.write_text('tampered')
            with self.assertRaises(RuntimeError):verify_manifest(root,seal,owner_uid=os.getuid())
    def test_manifest_rejects_unlisted_code(self):
        import hashlib
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory);manifest=root/'SOURCE-SHA256SUMS';manifest.write_text('');manifest.chmod(0o600)
            (root/'unreviewed.py').write_text('fixture')
            with self.assertRaises(RuntimeError):verify_manifest(root,hashlib.sha256(b'').hexdigest(),owner_uid=os.getuid())
    def test_report_seal_excludes_signing_material(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'report.json').write_text('{"result":"FAIL"}')
            (root/'signing.key').write_text('DISPOSABLE_CANARY_NOT_A_KEY')
            seal=seal_reports(root)
            self.assertEqual(len(seal),64);self.assertNotIn('signing.key',(root/'EVIDENCE-SHA256SUMS').read_text())
            with self.assertRaises(FileExistsError):seal_reports(root)
    def test_pickle_negative_control_executes_child_selected_callable(self):
        import pickle
        class Payload:
            def __reduce__(self):return (int,('42',))
        left,right=multiprocessing.Pipe()
        try:left.send_bytes(pickle.dumps(Payload()));self.assertEqual(right.recv(),42)
        finally:left.close();right.close()
    def test_safe_pipe_rejects_pickle_bytes(self):
        import pickle
        left,right=multiprocessing.Pipe()
        try:
            left.send_bytes(pickle.dumps({'fixture':True}))
            with self.assertRaises((ValueError,UnicodeError)):SafePipe(right).recv()
        finally:left.close();right.close()
    def test_safe_pipe_roundtrip_and_restricted_tags(self):
        left,right=multiprocessing.Pipe()
        try:
            a,b=SafePipe(left),SafePipe(right);value=('fixture',{'bytes':b'public','list':[1,True,None]})
            a.send(value);self.assertEqual(b.recv(),value)
            left.send_bytes(b'{"__g6j_type__":"eval","value":"7*6"}')
            with self.assertRaises(ValueError):b.recv()
        finally:left.close();right.close()
    def test_safe_pipe_partial_frame_deadline(self):
        left,right=multiprocessing.Pipe()
        try:
            os.write(left.fileno(),b'\x00')
            with self.assertRaises(TimeoutError):SafePipe(right,seconds=0.03).recv()
        finally:left.close();right.close()
    def test_safe_pipe_reconstructs_only_fixed_contract_types(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'repo'))
        from candidate_v3.contracts import Resource,Limits,StepContract
        value=StepContract(Resource('http://192.0.2.1:11434','fixture','fixture'),Limits(4096,64,16384,16384,20,60),'fixture','OFFLINE',(('temperature',0.1),))
        left,right=multiprocessing.Pipe()
        try:
            SafePipe(left).send(value);self.assertEqual(SafePipe(right).recv(),value)
        finally:left.close();right.close()
    def test_safe_pipe_in_fresh_role_process(self):
        context=role_context();left,right=context.Pipe();parent,child=SafePipe(left),SafePipe(right)
        process=context.Process(target=safe_child,args=(child,));process.start();child.close()
        try:
            result=parent.recv();process.join(10)
            self.assertEqual(process.exitcode,0);self.assertEqual(result['uid'],os.getuid());self.assertNotEqual(result['pid'],os.getpid())
        finally:
            parent.close()
            if process.is_alive():process.terminate();process.join()
    def test_suite_fixed_selection(self):
        command=suite_command('/fixture/python',Path('/fixture/temp'))
        self.assertNotIn('shell',command);self.assertIn('tests/execution/v3_redteam_test.py',command)
        self.assertEqual(command[4:8],['-p','pytest_asyncio.plugin','-p','no:cacheprovider'])
    def report_case(self,side_effect=None,code=0):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch('qualify_all.subprocess.run',side_effect=side_effect,return_value=NS(returncode=code)) as run:
                result=run_suite(['fixture'],cwd=root,env={},account=NS(pw_uid=os.getuid(),pw_gid=os.getgid()),output=root/'log',summary=root/'report',report={})
                self.assertEqual(json.loads((root/'report').read_text()),result)
                self.assertEqual(run.call_args.kwargs['extra_groups'],[])
                return result
    def test_timeout_retains_failed_report(self):self.assertEqual(self.report_case(subprocess.TimeoutExpired(['fixture'],900))['failure'],'SUITE_TIMEOUT')
    def test_failed_suite_cannot_report_pass(self):self.assertEqual(self.report_case(code=1)['result'],'FAIL')
    def test_launch_failure_retained(self):self.assertEqual(self.report_case(OSError())['result'],'FAIL')
    def test_success_is_explicit(self):self.assertEqual(self.report_case()['result'],'PASS')

if __name__=='__main__':unittest.main(verbosity=2)
