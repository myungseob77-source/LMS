# LMS approved design
User approved Windows 11, Python + LangGraph, harness → loop → graph,
VS Code integration, GitHub CI, and a PowerShell installer.
Harness injects an executor and verifier. Bounded loop shares steps with a
LangGraph plan → execute → verify graph. Demo is deterministic and offline;
it does not perform AI inference or modify arbitrary files. JSON result logs
remain local and ignored by Git. Provider adapters are future extensions.
Standard-library orchestration alone reduces dependencies but omits the requested
LangGraph foundation; LangGraph is selected for explicit state and branching.
Installation targets a user-writable folder and never overwrites an unrelated repo.
PC execution and interactive GitHub authentication happen on the user's Windows PC.
