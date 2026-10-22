"""Complete isolated consumer graph, never imported by production startup."""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .contracts import Refused,digest
from .legacy import RulesFirstL1
from .ownership import OwnedProvider
from .transport import NativeTransport
from .evidence import EvidenceBridge
from .lineage import HighWater
from .authority_client import ServiceAuthorityClient
from .checkpoints import CheckpointWriter
from .ingress import Ingress
from .topology import Topology

def build_isolated_app(runtime,*,api_token,allowed_origins,qualification):
    if (qualification!='OFFLINE_EVALUATION_ONLY' or type(runtime.legacy_policy) is not RulesFirstL1
        or type(runtime.provider) is not OwnedProvider or type(runtime.provider.provider) is not NativeTransport
        or type(runtime.evidence_bridge) is not EvidenceBridge or type(runtime.acceptance_guard) not in (HighWater,ServiceAuthorityClient)
        or type(runtime.checkpoint_writer) is not CheckpointWriter
        or type(runtime.provider.topology) is not Topology):raise Refused('INCOMPLETE_ISOLATED_GRAPH')
    runtime.acceptance_guard.check(runtime.store)
    @asynccontextmanager
    async def lifespan(app):
        runtime.acceptance_guard.check(runtime.store)
        try:
            yield
        finally:
            # ASGI tells us this is a lifespan shutdown, not who requested it.
            await runtime.drain(mechanism='LIFESPAN_SHUTDOWN')
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.mount('/',Ingress(runtime,api_token=api_token,allowed_origins=allowed_origins))
    return app


def build_protected_isolated_app(runtime,*,api_token,allowed_origins,qualification):
    """Mandatory protected graph. Historical builder remains for baseline tests only."""
    if (type(runtime.acceptance_guard) is not ServiceAuthorityClient
        or runtime.checkpoint_writer.highwater is not runtime.acceptance_guard
        or runtime.provider.store is not runtime.store):raise Refused('PROTECTED_GRAPH_REQUIRED')
    if digest(runtime.legacy_policy.memory_snapshot.encode())!='e4fc564a6b52728736b50165a78467a383be82dadfeebcb7fade43cdd8489c29':raise Refused('PROTECTED_MEMORY_SNAPSHOT')
    profiles=((runtime.legacy_policy.router,4096,64,20),(runtime.legacy_policy.responders['trivial'],4096,80,180),(runtime.legacy_policy.responders['normal'],8192,150,180))
    for contract,context,output,deadline in profiles:
        if (contract.limits.context,contract.limits.output,contract.limits.deadline,contract.limits.keep_alive)!=(context,output,deadline,60):raise Refused('PROTECTED_PROPOSED_PROFILE')
    app=build_isolated_app(runtime,api_token=api_token,allowed_origins=allowed_origins,qualification=qualification)
    runtime.provider.provider.authority_client=runtime.acceptance_guard
    return app
