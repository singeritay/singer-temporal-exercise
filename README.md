# singer-temporal-exercise

## Temporal Infra design
The `temporal_infra` package is designed as a small reusable SDK layer around Temporal worker bootstrap.

It separates responsibilities into focused components:
- `ConfigurationLoader`: loads environment-scoped values from YAML and validates them into typed models.
- `EnvironmentManager`: resolves the active environment from `ENV` (with a default).
- `TemporalWorker`: exposes a simple API to register workflows/activities and run a worker using loaded config.

##### Configuration is intentionally split by ownership:
- Infra-level values (for example `temporal_server_url`) are stored in `temporal_config.yml`, because they are environment/platform settings shared across services.
- App-level runtime inputs (for example `TASKS_QUEUE_NAME`) are not stored in YAML, because they are expected to be provided by SDK users (developers) per worker/service context.

##### Auto-wrapping functions as activities?
I've had an iteration in which the TemporalWorker automatically wrapped the functions as activities,
by that, I've given the user the option to pass a "plain function", instead of passing a Temporal activity.
Later, I've understood that the workflow should be built from different activities, not plain function,
so users will ultimately be required to wrap their functions with activity wrapper.