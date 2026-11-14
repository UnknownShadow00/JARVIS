"""Print inert R2 JSON; this program never starts a host command."""
import argparse,json,os,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bounded import read_fd
from common import decode,need
import packet as p
import collision

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True);parser.add_argument('--case',choices=p.CASES,required=True);args=parser.parse_args()
 fd=os.open(args.input,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:record=decode(read_fd(fd,1048576,time.monotonic()+3,owner=os.getuid()),1048576)
 finally:os.close(fd)
 need(record.get('kind')=='MANDATORY_STAGE2_PREFLIGHT','mandatory input schema')
 collision.absent(record['session'],args.case,record['collision'])
 plan=p.plan(record['session'],record['sample'],args.case,record['identity'],occupied=record['occupied'],used=record['used'])
 p.freshness(record['session'],record['sample'],plan)
 print(json.dumps({'authorization_granted':False,'proposal':plan,'command':p.command_envelope(plan['argv'],'create',record['session'],record['sample']),
 'observation_argv':p.observation_commands(record['session']['nonce'],args.case,record['session']['boot_id'])},indent=2))
if __name__=='__main__':main()
