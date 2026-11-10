# Tasks

- [x] Reject Azure-qualified models and remove Azure-specific mutations, with regression checks for other models.
- [x] Update knowledge and migration documentation and use a major version.
- [x] Validate targeted and release checks without weakening unrelated tests.

- Targeted provider tests passed (32 tests and four subtests). Wheel/sdist, Twine, OKF and OpenSpec validation passed. The full unit suite still has four unrelated retry API failures; publication remains blocked.

- Follow-up: 358 unit tests passed, with two existing skips; OKF and OpenSpec checks passed.
