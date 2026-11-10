"""Current public caller contract: canonical ID and authenticated shared writer."""
import uuid
from fastapi import FastAPI
from fastapi.testclient import TestClient
from application_fixtures import admitted_app
from app.agent.api import router
from app.config import settings

def test_public_caller_cannot_select_scope_or_complete(admitted_app,monkeypatch):
    monkeypatch.setattr(settings.server,'api_token','synthetic-caller')
    app=FastAPI();app.include_router(router)
    with TestClient(app,headers={'Authorization':'Bearer synthetic-caller'}) as c:
        key=str(uuid.uuid4());body={'request_id':key,'goal':'held'}
        assert c.post('/tasks',json={**body,'scope':'other'}).status_code==422
        assert c.post('/tasks',json=body).json()['scope']=='local-service'
        assert c.patch('/tasks/'+key,json={'status':'completed'}).status_code==405
        assert c.get('/tasks/'+key).json()['status']=='pending'
