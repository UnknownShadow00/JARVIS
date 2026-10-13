"""Pure source analysis: no app import, config/environment loader, or provider."""
import ast, collections, dataclasses, hashlib, json, re, sys, types
from pathlib import Path
r=Path(sys.argv[1])
inputs=('Hello. Reply briefly.','What is two plus two?','Name one primary colour.','Please give a brief friendly greeting.')
router=ast.parse((r/'app/brain/router.py').read_text())
rules=next(n for n in ast.walk(router) if isinstance(n,ast.FunctionDef) and n.name=='_classify_by_rules')
scope={'re':re,'RouterResult':collections.namedtuple('RouterResult','intent confidence suggested_tool reasoning')}
exec(compile(ast.Module(body=[rules],type_ignores=[]),'reviewed-router-rules','exec'),scope)
tree=ast.parse((r/'app/brain/complexity_router.py').read_text())
classes=[n for n in tree.body if isinstance(n,ast.ClassDef)]
scope.update(dataclass=dataclasses.dataclass,settings=types.SimpleNamespace(models=types.SimpleNamespace(main='qwen3-nothink',router='gemma3:4b')))
exec(compile(ast.Module(body=classes,type_ignores=[]),'reviewed-complexity-rules','exec'),scope)
direct={}
exec(compile((r/'app/brain/direct_responder.py').read_text(),'reviewed-direct-responder','exec'),direct)
rows=[]
for text in inputs:
    rule=scope['_classify_by_rules'](None,text)
    decision=scope['ComplexityRouter']().decide(text,'respond')
    reply=direct['try_direct_reply'](text)
    assert reply is None
    rows.append({'input':text,'direct_reply_available':False,'intent_rule':None if rule is None else rule.intent,'rule_confidence':None if rule is None else rule.confidence,'model_router_required':rule is None,'if_respond_complexity':dataclasses.asdict(decision)})
assert [v['if_respond_complexity']['model'] for v in rows]==['gemma3:4b','qwen3-nothink','qwen3-nothink','qwen3-nothink']
assert [v['model_router_required'] for v in rows]==[True,False,True,True]
sources=['app/brain/router.py','app/brain/complexity_router.py','app/brain/direct_responder.py','app/brain/prompts.py','app/brain/llm_client.py','app/server.py','app/config.py','config.yaml']
print(json.dumps({'method':'AST-isolated pure original rules; configured model names only; no real model output or effective environment claim','rows':rows,'sha256':{n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in sources}},indent=2))
