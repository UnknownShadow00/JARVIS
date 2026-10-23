import hashlib,io,json,os,pathlib,stat,subprocess,sys,tarfile,tempfile,unittest
from safe_payload import validate,materialize
from runtime_check import check_versions,distribution_set,check_library_origins
from verify_bundle import verify
from extract_bundle import extract
from gate6k_safe_extract import valid_name
class PreparationTests(unittest.TestCase):
    def test_all_gate6k_export_aliases(self):
        base=pathlib.Path(__file__).resolve().parents[1]
        rows=json.loads((base/'locks/gate6k-ARTIFACTS.json').read_text());self.assertEqual(len(rows),131)
        names=[r['filename'] for r in rows.values()];self.assertEqual(len(set(names)),131)
        for name in names:self.assertEqual(valid_name(name),name)
    def archive(self,entries):
        data=io.BytesIO()
        with tarfile.open(fileobj=data,mode='w') as t:
            for name,kind,mode in entries:
                m=tarfile.TarInfo(name);m.type=kind;m.mode=mode;m.linkname='outside';m.size=1 if kind==tarfile.REGTYPE else 0
                t.addfile(m,io.BytesIO(b'x') if m.size else None)
        data.seek(0);return tarfile.open(fileobj=data)
    def test_good_archive(self):
        with self.archive([('source/file',tarfile.REGTYPE,0o644)]) as t:self.assertEqual(len(validate(t)),1)
    def test_no_destination_on_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'new'
            with self.archive([('../escape',tarfile.REGTYPE,0o644)]) as t:
                with self.assertRaises(ValueError):materialize(t,p)
            self.assertFalse(p.exists())
    def test_preexisting_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=pathlib.Path(tmp)/'existing';dest.mkdir()
            with self.archive([('file',tarfile.REGTYPE,0o644)]) as t:
                with self.assertRaises(FileExistsError):materialize(t,dest)
    def test_regular_copy_sanitizes_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'new'
            with self.archive([('file',tarfile.REGTYPE,0o644)]) as t:materialize(t,p)
            self.assertEqual((p/'file').stat().st_mode&0o777,0o600)
    def test_exact_versions(self):check_versions({'a':'1'},{'a':'1'},(3,14,4),'3.46.1','x86_64')
    def test_duplicate_distribution_identity(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):distribution_set([('some_pkg','1'),('Some.Pkg','1')])
    def test_missing_library(self):
        with self.assertRaisesRegex(ValueError,'MISSING_OR_HOST_LIBRARY'):check_library_origins([],pathlib.Path('/private/lib'))
    def test_host_library_fallback(self):
        with self.assertRaisesRegex(ValueError,'MISSING_OR_HOST_LIBRARY'):check_library_origins(['/usr/lib/libsqlite3.so.0'],pathlib.Path('/private/lib'))
    def test_private_library_origins(self):check_library_origins(['/private/lib/'+n for n in ('libsqlite3.so.0','libseccomp.so.2','libcrypto.so.3','libssl.so.3')],pathlib.Path('/private/lib'))
    def test_wrong_python(self):
        with self.assertRaisesRegex(ValueError,'PYTHON'):check_versions({}, {},(3,14,5),'3.46.1','x86_64')
    def test_wrong_sqlite(self):
        with self.assertRaisesRegex(ValueError,'SQLITE'):check_versions({}, {},(3,14,4),'3.46.2','x86_64')
    def test_wrong_arch(self):
        with self.assertRaisesRegex(ValueError,'ARCHITECTURE'):check_versions({}, {},(3,14,4),'3.46.1','aarch64')
    def test_unexpected_distribution(self):
        with self.assertRaisesRegex(ValueError,'DISTRIBUTION'):check_versions({'a':'1'},{'a':'1','extra':'1'},(3,14,4),'3.46.1','x86_64')
    def test_missing_distribution(self):
        with self.assertRaisesRegex(ValueError,'DISTRIBUTION'):check_versions({'a':'1'},{},(3,14,4),'3.46.1','x86_64')
    def test_network_guard_child(self):
        r=subprocess.run([sys.executable,'-I','-B','-c','import sys;sys.path.insert(0,'+repr(str(pathlib.Path(__file__).parent))+');from offline_exec import deny_network;deny_network();print("denied")'],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),'denied')
    def manifest_fixture(self,root):
        p=root/'artifacts';p.mkdir();(p/'one').write_bytes(b'test')
        m=root/'SHA256SUMS';m.write_text(hashlib.sha256(b'test').hexdigest()+'  artifacts/one\n');return hashlib.sha256(m.read_bytes()).hexdigest()
    def test_manifest_ok(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);h=self.manifest_fixture(root);self.assertEqual(verify(root,h),1)
    def test_manifest_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);h=self.manifest_fixture(root);(root/'artifacts/one').write_bytes(b'bad')
            with self.assertRaises(ValueError):verify(root,h)
    def test_manifest_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);h=self.manifest_fixture(root);(root/'artifacts/one').unlink()
            with self.assertRaises(FileNotFoundError):verify(root,h)
    def test_manifest_unexpected(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);h=self.manifest_fixture(root);(root/'artifacts/extra').write_bytes(b'extra')
            with self.assertRaises(ValueError):verify(root,h)
    def test_manifest_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);h=self.manifest_fixture(root);(root/'artifacts/one').unlink();(root/'artifacts/one').symlink_to('/etc/hostname')
            with self.assertRaises(ValueError):verify(root,h)
    def test_manifest_wrong_anchor(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);self.manifest_fixture(root)
            with self.assertRaises(ValueError):verify(root,'0'*64)
    def bundle_case(self,entry=None,wrong_hash=False):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);arc=root/'bundle.tar'
            with tarfile.open(arc,'w',format=tarfile.USTAR_FORMAT) as t:
                m=tarfile.TarInfo('SHA256SUMS');m.mode=0o600;m.size=1;t.addfile(m,io.BytesIO(b'x'))
                if entry:
                    n,kind,mode=entry;m=tarfile.TarInfo(n);m.type=kind;m.mode=mode;m.linkname='outside';m.size=1 if kind==tarfile.REGTYPE else 0;t.addfile(m,io.BytesIO(b'x') if m.size else None)
            sha='0'*64 if wrong_hash else hashlib.sha256(arc.read_bytes()).hexdigest()
            if entry or wrong_hash:
                with self.assertRaises(ValueError):extract(arc,root/'dest',sha)
                self.assertFalse((root/'dest').exists())
            else:self.assertEqual(extract(arc,root/'dest',sha),1)
    def test_bundle_good(self):self.bundle_case()
    def test_bundle_wrong_hash(self):self.bundle_case(wrong_hash=True)
    def test_bundle_long_pax_name(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);arc=root/'bundle.tar'
            with tarfile.open(arc,'w',format=tarfile.PAX_FORMAT) as t:
                for name in ['SHA256SUMS','artifacts/'+('x'*120)]:
                    m=tarfile.TarInfo(name);m.mode=0o600;m.size=1;t.addfile(m,io.BytesIO(b'x'))
            self.assertEqual(extract(arc,root/'dest',hashlib.sha256(arc.read_bytes()).hexdigest()),2)
    def test_bundle_unknown_pax_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);arc=root/'bundle.tar'
            with tarfile.open(arc,'w',format=tarfile.PAX_FORMAT) as t:
                m=tarfile.TarInfo('SHA256SUMS');m.mode=0o600;m.size=1;m.pax_headers={'comment':'unexpected'};t.addfile(m,io.BytesIO(b'x'))
            with self.assertRaises(ValueError):extract(arc,root/'dest',hashlib.sha256(arc.read_bytes()).hexdigest())
for label,entries in {
 'absolute':[('/escape',tarfile.REGTYPE,0o644)],
 'parent':[('a/../escape',tarfile.REGTYPE,0o644)],
 'empty_component':[('a//file',tarfile.REGTYPE,0o644)],
 'backslash':[('a\\file',tarfile.REGTYPE,0o644)],
 'symlink':[('a',tarfile.SYMTYPE,0o644)],
 'hardlink':[('a',tarfile.LNKTYPE,0o644)],
 'device':[('a',tarfile.CHRTYPE,0o644)],
 'fifo':[('a',tarfile.FIFOTYPE,0o644)],
 'world_writable':[('a',tarfile.REGTYPE,0o666)],
 'setuid':[('a',tarfile.REGTYPE,0o4644)],
 'duplicate':[('a',tarfile.REGTYPE,0o644),('a',tarfile.REGTYPE,0o644)],
 'conflict':[('a',tarfile.REGTYPE,0o644),('a/b',tarfile.REGTYPE,0o644)],
}.items():
    def case(self,entries=entries):
        with self.archive(entries) as t:
            with self.assertRaises(ValueError):validate(t)
    setattr(PreparationTests,'test_reject_'+label,case)
for label,entry in {'absolute':('/bad',tarfile.REGTYPE,0o600),'parent':('../bad',tarfile.REGTYPE,0o600),
 'duplicate':('SHA256SUMS',tarfile.REGTYPE,0o600),'symlink':('bad',tarfile.SYMTYPE,0o600),
 'hardlink':('bad',tarfile.LNKTYPE,0o600),'device':('bad',tarfile.CHRTYPE,0o600),
 'fifo':('bad',tarfile.FIFOTYPE,0o600),'world_write':('bad',tarfile.REGTYPE,0o666),
 'setuid':('bad',tarfile.REGTYPE,0o4600),'conflict':('SHA256SUMS/bad',tarfile.REGTYPE,0o600)}.items():
    def case(self,entry=entry):self.bundle_case(entry)
    setattr(PreparationTests,'test_bundle_reject_'+label,case)
if __name__=='__main__':unittest.main(verbosity=2)
