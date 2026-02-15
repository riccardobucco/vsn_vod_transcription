# Technical Choices and Rationale

## Speckit (Spec-Driven Development)

I chose GitHub Speckit to anchor the project in Spec-Driven Development. The goal was to keep the system behavior and API surface explicit, testable, and aligned with the assignment requirements throughout the build.

Spec-Driven Development flips the script on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: specifications become executable, directly generating working implementations rather than just guiding them.

In practice, this meant using Speckit to keep product scenarios and predictable outcomes at the center of the workflow instead of improvising or "vibe coding" each part from scratch. It helped me validate the key flows early and keep the implementation aligned with the spec.

## Home Server Deployment

I deployed the app on my home server to have full control over the environment, persistent storage, and background workers, and to keep the deployment simple and reproducible. It also allowed me to iterate quickly and verify the full async pipeline (API + worker + storage) end-to-end without relying on a third-party hosting provider.

The service is reachable at `vsn.riccardobucco.com` for review and testing.
