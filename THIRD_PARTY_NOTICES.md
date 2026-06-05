# Third-Party Notices

This project bundles the following third-party open-source components in `runtime/`:

## scorm-again (v3.0.5)
- SCORM 1.2 / 2004 runtime API (LMS bridge).
- Author: Joshua P. (jcputney) — https://github.com/jcputney/scorm-again
- License: MIT
- Vendored build + integrity: see `runtime/VENDOR.lock`.

## lottie-web (lottie_light)
- Lottie animation player (loaded only when a course uses Lottie — opt-in).
- Author: Airbnb — https://github.com/airbnb/lottie-web
- License: MIT

GSAP (used by the optional HyperFrames video pipeline) is loaded from a CDN at render
time and is not redistributed by this repository.

All third-party components retain their original licenses.
