# Single source revert

Revert production commit 66c811277d563d953bf1e3ebe37e0c01ea278860. This removes observer and three new test/corpus files and restores all ten old structural functions, including pre-observation absence assumptions. Complete staged production patch reverse-apply check passed before commit. No runtime rollback, session/P2 cleanup, resource operation or persisted observation cleanup: producer is unwired and does not persist. Development sealed evidence and documentation history are retained.
