# Import and consumer proof

Evidence import-graph.json contains exact direct and transitive app edges. Direct passive dependencies: adapter's AdapterRequest/AdapterError/parse_recorded_response; classifier, router, lane, canonicalize, permissions, obligations, response; correlation data/ID validation; provenance snapshot/record validation; P0 types. Standard-library dependencies are passive data utilities.

Zero direct/indirect confirmation, dispatch, registry, server, provider-client or live Hermes runtime edge. No dynamic import, service locator, sys.modules retrieval, injected executable collaborator, clock read or identifier minting. Constructor bans prevent creation of invocation/result/projection in the composer.

All-app scan: pipeline importers zero; adapter importers exactly app/execution/pipeline.py; confirmation importers zero; dispatcher importers zero. Existing scans plus precise AST budgets prove the only new consumer relationships match P-B03/P-B04/P-B06. Canonicalizer owns normalization/version and pipeline only calls its existing API. No canonicalization logic copied.
