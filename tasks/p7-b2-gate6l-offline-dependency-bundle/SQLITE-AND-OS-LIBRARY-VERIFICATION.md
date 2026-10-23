# SQLite and OS library verification

Gate 6L — Nexus-only development evidence. No VM, privileged provisioning, production access, provider generation or pilot activity occurred. Historical Gate 6K source remains unchanged.

The selected OS is Ubuntu Server 26.04.1 amd64. The signed repository supplies the exact required Python and SQLite versions. This choice is verified for acquired artifacts and the Nexus installation rehearsal; guest boot/provisioning remains untested and requires authorization.

The interpreter reports `sqlite3.sqlite_version == "3.46.1"`. The mapped library is the private downloaded `libsqlite3.so.0`, from Ubuntu3.46.1-9ubuntu0.3. SQL `sqlite_source_id()` was recorded, including Ubuntu's `alt1` suffix. The system sqlite3 command was not used as proof. The signed Ubuntu library is the installation input; the official SQLite source archive is retained as an alternative review/build input with SHA256 `67d3fe6d268e6eaddcae3727fce58fcc8e9c53869bdd07a0c61e38ddf2965071`. No independent publisher signature was established for that source archive; no stronger claim is made.

`libseccomp2_2.6.0-2ubuntu5_amd64.deb` SHA256 is `c5e4b198f251da0ede226fd179830bd8767482821a1773f835358f726795cb16`. The downloaded library loads and reports2.6.0; process-local seccomp denies non-AF_UNIX socket creation without root or a host policy change. OpenSSL 3.5.5 and private libcrypto/libssl paths were observed. Runtime checks now refuse host fallback for SQLite, seccomp, crypto and SSL.

Ubuntu `cryptography 46.0.5-1ubuntu2.2` uses the distro CFFI backend. The signed `python3-cffi-backend2.0.0-3build1` satisfies the virtual backend API bounds and adds no extra Python distribution metadata. Ed25519 synthetic sign/verify passes. The same-version PyPI wheel requires a separate cffi distribution absent from the 127 pins and is deliberately not selected.

The signed ISO is2,927,861,760 bytes, SHA256 `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927`. Checksum signature fingerprint `843938DF228D22F7B3742BC0D94AA3F0EFE21092` matches [Ubuntu's verification documentation](https://documentation.ubuntu.com/security/software-integrity/image-verification/). The offline installer extracts selected regular payloads and copies reviewed SONAME targets as regular bytes. It never executes deb maintainer scripts or installs packages globally.
