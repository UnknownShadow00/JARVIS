import os,json,socket,subprocess,sys
from importlib.metadata import version
listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1)
client=socket.create_connection(listener.getsockname(),timeout=1);peer,_=listener.accept();client.close();peer.close();listener.close()
child=subprocess.run([sys.executable,'-I','-S','-c',"import os,json; before=os.getuid(); target=before+1\ntry:os.setuid(target);print(json.dumps({'changed_uid':True,'uid':os.getuid()}))\nexcept OSError as e:print(json.dumps({'changed_uid':False,'errno':e.errno,'exception':type(e).__name__}))"],capture_output=True,text=True,timeout=2)
print(json.dumps({'loopback_socket_in_isolated_namespace':'connected','uid_map':open('/proc/self/uid_map').read().strip(),'different_uid_attempt':json.loads(child.stdout),'uvicorn_version':version('uvicorn')}))
