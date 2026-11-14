"""Bounded offline evidence-file loading; hashes are checked against an external seal."""
import os,time
from common import need
from bounded import read_fd
import packet as p

def load(root, manifest):
    need(type(manifest) is dict and set(manifest)=={'cases/'+c+'.json' for c in p.CASES},'artifact paths')
    deadline=time.monotonic()+10
    # Caller independently trusts the selected evidence root's ancestry. The root
    # itself and every child are opened without following links.
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        sub=os.open('cases',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
        try:
            data={}
            for case in p.CASES:
                leaf=os.open(case+'.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=sub)
                try:data['cases/'+case+'.json']=read_fd(leaf,1048576,deadline,owner=os.getuid(),expected_sha=manifest['cases/'+case+'.json']['sha256'])
                finally:os.close(leaf)
            return data
        finally:os.close(sub)
    finally:os.close(fd)
