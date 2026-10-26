# Security policy

Publication draft: configure and verify the private reporting route before making this policy public.

## Supported versions

During alpha, the latest alpha release receives security fixes or explicit upgrade guidance. Earlier releases may require upgrading. Stable-release support windows will be documented before 1.0.

## Report a vulnerability

Use this repository's GitHub private vulnerability reporting feature once enabled and verified. Fallback private contact: **REPLACE_VERIFIED_SECURITY_CONTACT**. Do not open a public issue containing exploit details, live credentials or private traces.

Include affected version, supported environment, impact and a minimal synthetic reproducer. Maintainers aim to acknowledge reports within five business days on a best-effort basis; this is not a commercial SLA. Disclosure and remediation timing depend on severity, reproducibility and available maintainers.

## Scope and limitations

Fail2Test parses evidence and runs explicitly configured application code. The normal local process is not a sandbox for hostile repositories, dependencies, pytest plugins or runners. Mocked transport controls do not restrict every possible operation performed by arbitrary user code. Sanitization is best effort; review artifacts before sharing them.

Default local operations do not upload evidence or send telemetry. Future provider/hosted features require explicitly documented data processing and security controls.
