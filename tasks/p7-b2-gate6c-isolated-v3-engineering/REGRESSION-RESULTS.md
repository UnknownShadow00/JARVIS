# Fresh regression and developmental failures

| Run | Result | Meaning |
|---|---|---|
| focused-1 |67 passed,1 failed | fixture constructed duplicate verb argument; fixed test construction, not expected behavior |
| focused-2 |74 passed | early persistence/identity improvements |
| focused-3 |79 passed | canonical observer bridge and kernel canaries |
| full-1 |6725 passed,283 failed,25 errors,11 deselected; interrupted111.57s | sandbox denied safe root directory traversal; candidate app placement violated frozen graph; test poll lacked bound |
| full-2 |7248 passed,4 failed,11 deselected,2 warnings;23.61s | two deliberate child-kill tests denied by signal fence; two host-statistics tests denied by filesystem fence |
| harness-3 |9 passed in0.42s | narrowly verified disposable-child signal broker and fake host-statistics dependencies |
| focused-final (pre-privacy hardening) |93 passed in1.26s | pre-privacy candidate source |
| full-final (pre-privacy hardening) |**7259 passed,11 deselected,zero failures**,2 warnings,in24.02s (launcher24.237s) | all 7166 canonical baseline tests plus93 candidate tests |
| focused-sealed |**94 passed in 1.37s**, launcher1.433s | adds raw-content repr suppression test |
| full-sealed |**7260 passed,11 deselected,zero failures**,2 warnings,in 25.09s (launcher25.349s) | final sealed source:7166 canonical +94 candidate tests |

All run logs/results retained; failures were not removed or hidden. The same canonical11 deselections remain; no new security-test exclusion was added. Changes to the qualification harness are explicit: root READ_DIR without file access; standalone candidate outside the frozen app graph; bounded polling waits; two test modules get synthetic host statistics; exactly two verified disposable writer children may be killed through a pidfd broker. Original 208 test files and 119 app files remain unchanged. A passing frozen graph on the standalone package is not approval to integrate its new consumers into app.

Final full root audit:12 approved offline fixture subprocess launches;15 localhost DNS attempts blocked before resolution/send in existing error-path tests;0 credential/production access attempts;0 external writes;0 rejected nonfixture execution. Focused root audit: all those counts0. Direct libc canaries are separate intentional kernel denials. Successful external/provider transmissions 0. Child restrictions are inherited; killed fault-injection children cannot emit an atexit audit. Two benign dependency deprecation warnings remain; no package changes made.

Historical full suite 7166/11 is not relabeled as a new result. Golden remains historical12/20 with the same eight established failures; no model-capable Golden or digest run occurred. Historical legacy digest remains `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`; it was not regenerated. No claim about new stochastic-model compatibility follows from fake-backend regression.
