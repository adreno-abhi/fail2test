# Fail2Test

Fail2Test turns supported agent failures into reviewed, portable regression tests. It runs your current application code with controlled model/tool fixtures and exports ordinary pytest tests.

**Current status:** [v0.1.0 is publicly released](https://github.com/adreno-abhi/fail2test/releases/tag/v0.1.0).
The supported synchronous fixture workflow, native LangGraph adaptation and local browser UI
are implemented and checked on Windows/Ubuntu. Install from the tagged source checkout; no PyPI
upload has been made. Optional provider-based suggestions require explicit request consent.

Start with the [key-free quickstart](quickstart.md), then [integrate a runner](integration.md). Read [contracts and safety](contracts.md) before using private evidence or a downloaded case.

First check [application fit](adoption.md). For your own incident, use
[evidence preparation](evidence.md); arbitrary logs/vendor exports are not accepted directly.

Prefer visual review? Use the bundled [local browser UI](local-ui.md) for evidence, review,
execution results, reduction comparison and pytest export with the same engine.

The default workflow needs no model account, daemon, database or cloud service. It does require trusted application code with explicit dependency injection. A trace alone cannot reproduce every hidden state or side effect.

For a concrete failure-to-test story, follow the
[duplicate tool action walkthrough](duplicate-tool-regression.md).
