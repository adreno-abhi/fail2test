# Fail2Test

Fail2Test turns supported agent failures into reviewed, portable regression tests. It runs your current application code with controlled model/tool fixtures and exports ordinary pytest tests.

**Current status:** private pre-release preparation. The offline workflow, native synchronous LangGraph
adaptation, local browser UI and optional provider-based rule suggestions are implemented.
Hosted CI on Windows/Ubuntu and the installed browser/package workflow pass. Broader platform
coverage and public-launch work remain pending; no public release has shipped.

Start with the [key-free quickstart](quickstart.md), then [integrate a runner](integration.md). Read [contracts and safety](contracts.md) before using private evidence or a downloaded case.

First check [application fit](adoption.md). For your own incident, use
[evidence preparation](evidence.md); arbitrary logs/vendor exports are not accepted directly.

Prefer visual review? Use the bundled [local browser UI](local-ui.md) for evidence, review,
execution results, reduction comparison and pytest export with the same engine.

The default workflow needs no model account, daemon, database or cloud service. It does require trusted application code with explicit dependency injection. A trace alone cannot reproduce every hidden state or side effect.
