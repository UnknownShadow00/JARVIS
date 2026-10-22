"""Native Ollama HTTP implementation. No default socket transport or discovery factory.
An explicit httpx transport and exact contracts are mandatory. Qualification uses mocks.
"""
import asyncio,time,math
import httpx
from .contracts import Refused,ProviderResult,ProviderRequest,canonical,digest,strict_json,decode

class _BorrowedTransport(httpx.AsyncBaseTransport):
    def __init__(self,transport):self.transport=transport
    async def handle_async_request(self,request):return await self.transport.handle_async_request(request)
    async def aclose(self):pass

class NativeTransport:
    def __init__(self, contracts, *, transport, clock=time.monotonic):
        if not isinstance(transport,httpx.AsyncBaseTransport):raise Refused('EXPLICIT_TRANSPORT_REQUIRED')
        self.contracts={c.resource:c for c in contracts}
        if len(self.contracts)!=len(contracts):raise Refused('DUPLICATE_RESOURCE')
        self.transport,self.clock=transport,clock
        self.authority_client=None

    async def aclose(self):
        await self.transport.aclose()

    async def request(self, request, *, ownership=None):
        contract=self.contracts.get(request.resource) if type(request) is ProviderRequest else None
        if contract is None:raise Refused('TRANSPORT_RESOURCE')
        from app.brain.model_ownership import GenerationLeaseV1,ModelResourceKeyV1
        if (type(ownership) is not GenerationLeaseV1 or ownership.resource!=ModelResourceKeyV1('ollama',request.resource.endpoint,request.resource.model)
            or ownership.operation_id!=request.substep):raise Refused('TRANSPORT_OWNERSHIP_REQUIRED')
        if any(type(v) is not str or len(v)!=32 or any(c not in '0123456789abcdef' for c in v) for v in (request.attempt,request.substep)):raise Refused('TRANSPORT_CORRELATION')
        if type(request.body) is not bytes or len(request.body)>contract.limits.request_bytes or digest(request.body)!=request.request_digest:raise Refused('TRANSPORT_REQUEST_BYTES')
        v=strict_json(request.body)
        options={'num_ctx':contract.limits.context,'num_predict':contract.limits.output}
        options.update(dict(contract.native_options))
        # Canonical observer requests are independently checked by CanonicalObserver;
        # native tools schema is allowed only on its frozen resource/profile.
        granite=contract.resource.profile=='jarvis.p7.ollama.granite41.b1r2.v1'
        required={'model','messages','stream','think','keep_alive','options'}
        if (type(v) is not dict or set(v) != (required|({'tools'} if granite and 'tools' in v else set()))
            or v.get('model')!=contract.resource.model or v.get('stream') is not False or v.get('think') is not False
            or type(v.get('keep_alive')) is not int or v['keep_alive']!=contract.limits.keep_alive
            or v.get('options')!=options or type(v.get('messages')) is not list or not v['messages']
            or any(type(m) is not dict or set(m)!={'role','content'} or m['role'] not in ('system','user','assistant') or type(m['content']) is not str for m in v['messages'])):
            raise Refused('NATIVE_REQUEST_SCHEMA')
        remaining=request.deadline-self.clock()
        if type(remaining) not in (int,float) or not math.isfinite(remaining) or remaining<=0 or remaining>contract.limits.deadline+0.01:raise Refused('TRANSPORT_DEADLINE')
        try:
            if self.authority_client is not None:self.authority_client.dispatch_once(request)
            ownership.claim_transport()
            async with asyncio.timeout(remaining):
                async with httpx.AsyncClient(transport=_BorrowedTransport(self.transport),trust_env=False,follow_redirects=False,timeout=remaining) as client:
                    async with client.stream('POST',contract.resource.endpoint+'/api/chat',content=request.body,
                            headers={'Content-Type':'application/json','Accept':'application/json','Accept-Encoding':'identity'}) as response:
                        if response.status_code!=200:raise Refused('NATIVE_HTTP_STATUS')
                        headers=response.headers
                        ct=headers.get_list('content-type');cl=headers.get_list('content-length');te=headers.get_list('transfer-encoding')
                        if len(ct)!=1 or ct[0].lower().split(';')[0].strip()!='application/json':raise Refused('NATIVE_MIME')
                        if len(cl)>1 or len(te)>1 or cl and te or te and te!=['chunked']:raise Refused('NATIVE_FRAMING')
                        if headers.get('content-encoding','identity')!='identity':raise Refused('NATIVE_ENCODING')
                        length=None
                        if cl:
                            if not cl[0].isascii() or not cl[0].isdigit():raise Refused('NATIVE_FRAMING')
                            length=int(cl[0])
                            if length>contract.limits.native_bytes:raise Refused('NATIVE_RESPONSE_LIMIT')
                        chunks=[];size=0
                        async for chunk in response.aiter_raw():
                            size+=len(chunk)
                            if size>contract.limits.native_bytes:raise Refused('NATIVE_RESPONSE_LIMIT')
                            chunks.append(chunk)
                        if length is not None and size!=length:raise Refused('NATIVE_INCOMPLETE_BODY')
                        body=b''.join(chunks);value=strict_json(body)
                        if (type(value) is not dict or value.get('done') is not True or value.get('model')!=contract.resource.model
                            or type(value.get('message')) is not dict or value['message'].get('role')!='assistant'
                            or type(value['message'].get('content')) is not str or 'error' in value):raise Refused('NATIVE_TERMINAL_SHAPE')
                        # A complete correlated done=true envelope is terminal evidence even
                        # when the caller subsequently rejects unsafe content.
                        return ProviderResult(request.attempt,request.substep,request.resource,request.request_digest,body,True)
        except asyncio.CancelledError:raise
        except Exception:raise Refused('NATIVE_TRANSPORT_UNCERTAIN') from None
