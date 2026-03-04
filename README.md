# singer-temporal-exercise

## How to run?

In order to run and be able to calculate results, we use `minikube` to deploy to local k8s cluster. <br>
We need to run temporal server, a worker for each math operation, a worker for calculation workflow, and a server to
trigger the workflow and return the results <br>

to run it - follow these steps (depends on having `minikube`):<br>

1. Run the deploy_script.sh (or .ps1 on Windows powershell) - this stage deploys all workers to the local cluster
2. Get the url for the trigger server - run `minikube service trigger-server --url`
3. Run a GET request for the trigger server - example `curl http://127.0.0.1:64366/calculate?expression=90%2B2` - runs
   the calculation 90 + 2

## Temporal Infra design

The `temporal_infra` package is designed as a small reusable SDK layer around Temporal worker bootstrap.

It separates responsibilities into focused components:

- `ConfigurationLoader`: loads environment-scoped values from YAML and validates them into typed models.
- `EnvironmentManager`: resolves the active environment from `ENV` (with a default).
- `TemporalWorker`: exposes a simple class to register workflows/activities and run a worker using loaded config.

#### Configuration is intentionally split by ownership:

- Infra-level values (for example `temporal_server_url`) are stored in `temporal_config.yml`, because they are
  environment/platform settings shared across services.
- App-level runtime inputs (for example `TASKS_QUEUE_NAME`) are not stored in YAML, because they are expected to be
  provided by SDK users (developers) per worker/service context.

#### Auto-wrapping functions as activities?

I've had an iteration in which the TemporalWorker automatically wrapped the functions as activities,
by that, I've given the user the option to pass a "plain function", instead of passing a Temporal activity.
Later, I've understood that the workflow should be built from different activities, not plain function,
so users will ultimately be required to wrap their functions with activity wrapper.

#### Liveness and readiness probes

I've implemented a liveness probe that sends a log every 10 seconds hinting that the worker is alive (push probe). In
addition, I've exposed a /metrics route (port 9000) on the worker using Temporal's Prometheus endpoint to allow for
external scraping of worker health and performance.
Readiness probe is currently implemented as a log that is written with the worker's startup.

#### One math worker code - multiple deployments

I've written a robust math activity worker (inside `caclulatr/workers`),
and I use different deployments to run different workers that will listen to different task queues.<br>
By that, I've successfully followed the instruction that
`Each operator type must be executed by a different worker and task queue`
without duplicating any code.

## Calculator Implementation

#### Scope Exclusions

The following topics are intentionally out of scope for this exercise:

- minus sign at start of number is not acceptable (except of the first number) (example: `-5 + (2 * -3) ^ 2` will not
  work. correct way - `-5 + (2 * (-3)) ^ 2`)
- Division-by-zero is not implemented - I don't raise a valid error to the user (the workflow fails as-is).
- Input validation for invalid characters is not implemented (unrecognized characters may be ignored by parsing).

#### How the calculation workflow executes

1. The workflow receives a single expression string.
2. It tokenizes the expression into numbers, operators, and parentheses.
3. It repeatedly resolves the innermost parenthesized part first (`(...)`), evaluates it, and replaces it with the
   result.
4. After all parentheses are resolved, it evaluates the flat expression by precedence groups:
   `^`, then `*`/`/`, then `+`/`-`.
5. Every binary operation is executed through a Temporal activity call, and each operator is routed to its matching
   task queue (`addition-queue`, `subtraction-queue`, etc.).
6. The final numeric result is returned by the workflow and then by the trigger server API.

## LLM Usage

Usually, I haven't used LLM as `build me this complete class`. Mostly, I've used it as helper for specific functions.
Almost every prompt is documented in `prompt.txt`.
In addition, I've used Gemini to learn about temporal and about "Platform thinking \ designing".
For code snippets and full implementation I've used Codex inside PyCharm.
