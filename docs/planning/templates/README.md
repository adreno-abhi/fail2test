# Publication templates

Historical drafts: the actual repository now has root community policies and `.github/`
issue/PR forms. Those root files are authoritative for current contribution and support
behavior. These planning drafts may describe superseded setup choices; do not copy them
over the current files. Public identity/contact and host verification remain publication gates.

These are drafts to adapt into a future implementation repository. Their presence does not establish a working support channel, security program, CLA/DCO check, protected branch or release pipeline.

Before publishing, replace every `REPLACE_*` token with a verified value, copy `repository/LICENSE.apache-2.0.txt` to the implementation repository's `LICENSE`, add applicable notices, enable the referenced GitHub features, and test contributor instructions against the actual package. The license reference is the exact official text downloaded from apache.org. The code of conduct should use a recognized full policy with working enforcement contacts; the provided policy setup file is a checklist rather than a substitute.

Files under `repository/` are intended root-level community drafts. Files under `github/` are intended `.github/` drafts. No workflow YAML is provided here because publishing/security configuration must be generated against the actual repository identity and verified in implementation.
