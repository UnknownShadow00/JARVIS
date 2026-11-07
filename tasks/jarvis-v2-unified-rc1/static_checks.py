"""Read public source only; no application imports or installed configuration."""
from pathlib import Path
import ast,json,hashlib,subprocess
P=Path(__file__).resolve().parent;W=P.parents[2]/'JARVIS-unified-rc1'
parsed=[]
for directory in ['app','tests','scripts','evals']:
 for f in sorted((W/directory).rglob('*.py')):
  ast.parse(f.read_text(),filename=str(f));parsed.append(str(f.relative_to(W)))
result={'python_AST_parsed':len(parsed),'parsed_files':parsed,'git_diff_check':subprocess.run(['git','diff','--check'],cwd=W,capture_output=True,text=True).returncode,'application_imported_on_host':False,'production_config_read':False,'fresh_advisory_audit_claimed':False,'typecheck':'No installed project typechecker qualified; not run','lint':'AST parsing and git whitespace checks only; full lint not claimed','coverage':'Full selected case accounting; line/branch coverage percentage not measured'}
# Source-only context review checks both allowlist and explicit nested exclusions.
patterns=(W/'.dockerignore').read_text().splitlines()
required=['**','!Dockerfile','!requirements-core.txt','!config.yaml.example','!app/','!app/**','!assets/','!assets/**','!frontend/','!frontend/**','**/.env','**/.env.*','**/*.key','**/*.pem','**/*.db','**/*.sqlite*','**/config.yaml','**/*credential*','**/node_modules/','**/__pycache__/']
assert all(x in patterns for x in required)
result['docker_context']={'required_rules_present':required,'excluded_top_level':['.git','tasks','data','logs','models','piper','jarvis-vault','config.yaml','.env'],'allowed_COPY_inputs':['requirements-core.txt','app','assets','frontend','config.yaml.example'],'real_image_build_run':False,'rule_matcher_qualification':'Static rule/order and Dockerfile COPY review, not a daemon build or full Docker matcher implementation'}
(P/'STATIC-CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='parsed_files'},indent=2))
