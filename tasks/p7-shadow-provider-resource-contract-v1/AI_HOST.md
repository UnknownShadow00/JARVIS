# Observed AI host and inactive-state limitation

SSH authenticated as jarvis to the operator-named AI host; the initial default nexus account was denied, without password attempts or security changes. OS reports Ubuntu 26.04 LTS. GPU inventory reports NVIDIA GeForce RTX 5090, 32607 MiB total, 0 MiB used, driver 580.178.04. MemTotal=31,493,500 kB, about 30.04 GiB usable guest RAM; inventory is not a measurement of maximum model RAM demand. Preserve the operator's hard 32 GB system-RAM allocation ceiling, without raising RAM or changing GPU assignment.

Ollama's installed binary contains the 0.31.2 version literal and its SHA-256 is recorded. Historical sealed AI preflight reports 0.31.2. Because executing Ollama/API calls is prohibited, this is installed-file corroboration, not a fresh /api/version assertion.

Existing AI service: ActiveState=active, MainPID=1370, NRestarts=0; process inventory contains /usr/local/bin/ollama serve and no model runner. Core remains zero Ollama processes. No Hermes processes observed on either host. Literal whole-host Ollama-inactive acceptance is unmet. Existing idle service is not evidence of a session model invocation; report both facts without relabeling it disabled.
