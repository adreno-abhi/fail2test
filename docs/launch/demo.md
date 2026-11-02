# What the demonstration shows

The [MP4](assets/fail2test-demo.mp4) and [GIF](assets/fail2test-demo.gif) record the real local
UI from version 0.1.0, source `b1b722c957336d59721f6a19c6fd616576960c7c`, against an isolated
synthetic refund workspace. Only loopback requests were observed. No model provider or
real refund/payment service was contacted. No production evidence or personal identity is used.

| Approximate time | Recorded action |
| --- | --- |
| 0–5 seconds | Open the key-free included example |
| 5–8 seconds | Inspect supported recorded failure evidence |
| 8–13 seconds | Review the at-most-one-refund assertion |
| 13–17 seconds | Reproduce the selected failing baseline |
| 17–21 seconds | Run the broken demo runner; regression fails |
| 21–25 seconds | Choose the supplied fixed demo runner; the same case passes |
| 25–end | Preview and save pytest plus reviewed JSON fixtures |

The demonstration does **not** generate a code fix. The bundled `broken` and `fixed`
runners already exist. For a real application, the developer fixes their implementation
and reruns the same runner/case. Reduction and optional model-assisted suggestions are not
shown in this short clip. The recorded elapsed time is presentation pacing, not a human
onboarding or integration-time benchmark.

The saved exported test was then executed separately with pytest and passed. Its execution
is verified in the local recording record; no terminal pytest result is shown in the clip.
Do not imply the UI itself ran pytest or displays a live-model quality score.

The MP4 has explanatory captions burned into an added strip below the actual viewport.
The GIF is a lower-frame-rate derivative for repository display. The separate VTT retains
caption text. No application status, rule result or UI behavior was edited for the video.

Media was recorded using the repository's existing Python Playwright/Chromium tooling and
transcoded with an isolated imageio-ffmpeg tool environment. No runtime dependency or lock
change was made. Original frames, capture script and execution record remain under ignored
`output/playwright/launch-demo/` and `local-artifacts/launch-materials/`.

The social-preview card is a project graphic rendered from the included HTML, using the
existing ink/green/paper palette and local system fonts. It is not a screenshot or a claim
of an independent customer result. PNG dimensions are 1280×640; the file is under 1 MB.
Uploading it to GitHub settings remains a separately approved external action.
