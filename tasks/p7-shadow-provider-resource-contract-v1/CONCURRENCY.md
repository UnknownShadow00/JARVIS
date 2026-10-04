# Approved shadow cap

Maximum simultaneous shadow model generations on the selected AI runtime: 1. This is a formal-P7 V1 cap, not a product limit and not a cap on existing legacy work. A future scheduler must account for requests until generation actually ends, including cancellation/timeout races. Cancelling a local waiter alone does not prove the remote generation stopped.

No queue bound, timeout, shadow retry or resource manager integration is selected here. The unresolved shared-host ownership relationship prevents treating the single-generation cap as a complete isolation proof.
