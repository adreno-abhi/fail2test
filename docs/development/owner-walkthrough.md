# Owner sample UI walkthrough

26 October 2026. The owner confirmed the sample flow through saving an export with
“done”, then approved GitHub setup preparation. This confirms a guided sample walkthrough;
it is not authorization to publish or a measured independent integration trial.

Two first-use issues were found and corrected before confirmation:

1. Upload requirements and the available example were unclear. Commit `993c7bf` added
   explicit accepted-format guidance and no-upload demo entry points, including the
   no-sample workspace case. All nine browser tests passed.
2. Save export was disabled without sufficient next-step guidance. The actual screen
   showed `VALIDATION_REQUIRED` for a reviewed case lacking a current reproduced baseline.
   Commit `98e3afe` added guidance for review, baseline reproduction, exact preview and
   saved export states. The browser regression first failed without this guidance, then
   all nine browser tests passed with it. Review and preview guards were preserved.

The confirmed path is import → review/approve → reproduce broken baseline → run fixed
regression → preview and save export. Known sample assertions/runners are synthetic and
key-free. The user encountered prerequisite explanations with assistance; do not describe
this as an unassisted usability study. Under-ten-minute sample onboarding and under-thirty-
minute integration targets were not measured for this human trial. Independent adoption
of the native example into a user's own application also remains unmeasured.
