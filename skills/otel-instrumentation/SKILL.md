---
name: otel-instrumentation
description: "Use when adding, migrating, or auditing OpenTelemetry instrumentation for frontend, mobile, backend, databases, Kafka, RabbitMQ, and external calls. Implement correlated traces, structured logs, application metrics, and verified OTLP export."
---

# OpenTelemetry Application Instrumentation

Instrument application behavior and every relevant dependency, not just SDK startup.
Apply this workflow to new instrumentation, missing spans, broken log correlation,
RUM/Embrace integration, and migrations from another telemetry SDK.

## Load The Relevant References

- Always read [signal and correlation rules](./references/signals-and-correlation.md).
- Read [dependency instrumentation](./references/dependencies.md) for every backend,
  worker, database, cache, message broker, or outbound integration in scope.
- Use current official documentation for the selected language, SDK distribution,
  instrumentation packages, and semantic-convention version. Do not treat these
  instructions as a package-version compatibility matrix.

## Non-Negotiable Rules

- Keep business behavior unchanged: no new writes, retries, acknowledgements,
  commits, exception swallowing, or authentication changes for observability.
- Prefer supported auto-instrumentation, driver hooks, and logging bridges. Add
  manual spans only for missing boundaries or meaningful business operations.
- Assign one owner per trace/log/metric provider, context manager, propagator, and
  physical dependency operation. Do not stack duplicate HTTP/DB/broker spans.
- A vendor SDK such as Embrace can own traces/logs while a separate OTel provider
  owns metrics. Verify actual signal support instead of assuming all three exist.
- Do not send tokens, passwords, connection strings, SQL parameters, message
  bodies, request/response bodies, user input, or arbitrary exception messages.
- Never disable TLS validation. Never install system packages, enable paid/cloud
  ingestion, expose a Collector publicly, or change infrastructure ownership
  without authorization. Preserve unrelated work and existing deployment routes.
- Do not invent context for unrelated work or claim guaranteed crash delivery.

## 1. Discover One Real Workflow

Start at a concrete request, handler, screen action, job, or failed telemetry check.
Inspect the controlling implementation, existing SDK setup, and nearby tests.
Identify runtime/language/framework versions, deployment model, logging framework,
current telemetry backend, privacy constraints, and allowed installation scope.
Ask only about decisions not recoverable from code or configuration.

Build a dependency coverage table before implementation:

| Boundary / concrete client | Instrumentation owner | Trace and propagation | Logs and metrics | Evidence / gap |
| --- | --- | --- | --- | --- |
| Browser/mobile action and API client | SDK or interceptor | CLIENT + W3C | Correlated operation logs, duration/count | Test or pending |
| Backend HTTP/RPC entry | Server middleware/agent | SERVER, extracted context | Request outcome, RED metrics | Test or pending |
| Each SQL/NoSQL/cache client | Driver hook/agent | CLIENT under operation | Failure, latency, pool/cache metrics | Test or pending |
| Each producer and consumer | Broker instrumentation | Creation context, links/parent policy | Processing/retry/settlement metrics | Test or pending |
| External HTTP, RPC, storage, search, jobs | Library hook or manual boundary | Propagated or linked context | Outcome and bounded measurements | Test or pending |

Enumerate actual libraries, not only infrastructure names: an ORM and raw SQL path,
two Redis clients, or a worker in another process can need separate coverage.
Mark absent systems N/A and unsupported instrumentation as a gap; do not add a
database or broker merely to satisfy this skill.

## 2. Establish The Telemetry Contract

1. Choose stable `service.name`, `service.namespace`, `service.version`, and
   `deployment.environment.name`, consistently across all three signals. Use
   `service.instance.id` only where deployment identity requires it; do not replace
   an existing resource wholesale or add unapproved user/device identifiers.
2. Choose SDK/agent versus distribution ownership and a documented compatible set
   of API, SDK, exporter, auto-instrumentation, runtime, and native dependencies.
   Inspect published artifacts and lockfiles, not only upstream main-branch docs.
3. Agree span boundaries, route/query/destination templates, severity/outcome
   policy, metric names/units/buckets, sampling, retention, and privacy allowlists.
   Follow the selected semantic conventions; do not silently mix old/new schemas.
4. Define each signal's Collector route and transport. Generic OTLP/HTTP base URLs
   may append `/v1/traces`, `/v1/logs`, `/v1/metrics`; per-signal endpoints normally
   include the full signal path. Check exporter behavior to avoid doubled paths.
5. Set parent-based trace sampling where appropriate, metric export/scrape
   intervals, queue/attribute/event limits, exporter timeouts, and bounded flush.
   Document error-log retention separately from trace sampling.

## 3. Bootstrap And Export Safely

- Initialize once and before instrumented clients/framework imports when required
  by the selected SDK. Register custom exporters/processors before SDK start.
- Integrate existing logging rather than replacing the application's logger.
  Libraries normally use OTel APIs; the application owns SDK configuration.
- Configure W3C `traceparent`/`tracestate`; enable baggage only with an explicit,
  small allowlist. Treat incoming context as untrusted and validate via propagators.
- Use managed secrets for server export auth; use an approved HTTPS ingestion
  gateway for public clients. Configure reverse proxy, authentication, origin/CORS,
  CSP, quotas, size limits, and rate limits without exposing backend credentials.
- Confirm Collector receivers and traces/logs/metrics pipelines are enabled, with
  bounded batching, memory limiting, export routing, and retry/queue policies.
  Reuse deployed Collector/backend components unless a change is authorized.
- Exclude telemetry export requests and diagnostic endpoints from instrumentation
  that would recursively instrument their own exports. Never filter out business
  dependency calls accidentally; test the exclusion rules.
- Telemetry failure must not fail application startup or block normal requests.
  Bound overhead and isolate exporter errors; avoid logging exporter failures back
  through the same failing pipeline indefinitely.
- Flush on graceful shutdown, serverless invocation completion, and appropriate
  mobile/browser lifecycle boundaries with a deadline. Do not shut down a shared
  provider on every request. Rotate exporters safely during config changes.

## 4. Instrument Backend Workflows

- Cover inbound HTTP/gRPC, meaningful application operations, all actual data
  access paths, producers/consumers, outbound calls, and background execution.
- Keep context active through async awaits, callbacks, executor/thread boundaries,
  goroutines, reactive streams, and task schedulers. Scope logs and metrics to the
  operation, then restore previous context in `finally`/equivalent cleanup.
- A synchronous client span encloses the actual call and relevant response/body
  consumption; server spans enclose request handling. Model long-lived streams,
  transactions, retries, and background work explicitly instead of inventing time.
- Mark failed operations per protocol conventions; do not equate every exception
  or every HTTP 4xx with a server failure. Re-throw/preserve original behavior.
- Instrument domain results such as accepted/rejected/unknown write outcome
  without claiming a write failed when the transport cannot establish its result.
- Use the [dependency rules](./references/dependencies.md), including infrastructure
  metrics collected outside the application where needed.

## 5. Instrument Frontend And Mobile Systems

- Browser: initialize before app bootstrap; instrument fetch/XHR or the framework
  interceptor, not both for the same physical request. Keep route templates, not
  concrete entity IDs, URLs, query strings, page titles, or form contents.
- Propagate context only to approved API origins. Check CORS/preflight acceptance
  of trace headers, expose response headers only if needed, and preserve CSP.
  Do not inject credentials or internal baggage into third-party requests.
- SSR/server code and browser code have different runtimes/resources. Keep browser
  SDKs out of server execution; explicitly model SSR-to-browser/hydration links if
  supported rather than assuming an active context survives serialization.
- Capture framework-handled errors, uncaught errors, unhandled rejections, and
  bootstrap failures through their actual hooks. Preserve framework handlers;
  avoid double-reporting events seen by multiple hooks. Test real browser events,
  especially Zone.js, worker, iframe, and cross-origin cases.
- Measure user-visible operations and appropriate Web Vitals, startup/screen
  performance, network durations, and errors. Do not treat a console message or
  an auto-instrumentation being enabled as proof that data is exported.
- Mobile: initialize at application/process scope; cover lifecycle, network,
  JVM/managed errors, native crashes, and ANR/hangs according to actual SDK support.
  Distinguish verified paths from opt-in or unsupported native features.
- For crash persistence, sanitize before local storage, bound size/count/retention,
  save before asynchronous queues can be lost, replay on next launch, and remove
  only under a documented acknowledgement policy. SDKs may maintain separate state.
  Collector acceptance is not durable storage; replay may duplicate reports.
- Browser/mobile shutdown, OOM, force-stop, OS kill, and tab termination can bypass
  telemetry. Use best-effort lifecycle export and document limits. Handle sourcemaps,
  R8/ProGuard mappings and native symbols under approved privacy/storage policies.
- With Embrace/RUM vendors, explicitly choose standalone/custom OTLP or cloud mode;
  configure signal support, resources, exporters and mapping uploads accordingly.
  Do not claim a generic trace UI supplies the vendor's crash/session analytics.

## 6. Verify Incrementally And End To End

After the first small edit, run the narrowest relevant compile/test before widening.
Use real SDK in-memory exporters plus serialization/integration checks, not only
mocked initialization. Run the repository's required build, lint and security gates.

Verify the following for systems present in scope:

- One real frontend/API request has the expected CLIENT/SERVER parent IDs and no
  duplicate physical-call spans. DB/cache spans and external calls attach correctly.
- A log emitted inside an active child span retains its exact trace/span IDs on the
  wire and in storage; concurrent requests/messages never exchange contexts.
- Kafka/RabbitMQ propagation, batch links, processing, redelivery and settlement
  match the documented model. Broker lag/depth metrics have a working source.
- Success, timeout, connection failure, cancellation, dependency outage, retries,
  transaction rollback, and shutdown preserve application behavior and correct counts.
- Metrics show correct units, counts, latency buckets and bounded dimensions;
  exemplars link to retained traces where the full toolchain supports them.
- Synthetic sensitive markers are absent from actual exported spans/logs/resources,
  events, links and metric labels. Verify getters/metadata survive custom projections.
- Collector outage causes bounded loss/retry, not unbounded queues, UI hangs,
  duplicate writes, recursive exports, or application failures.
- Record clock offsets, parent IDs and raw timestamps when a timeline looks wrong.
  Compare host/container/emulator clocks with transport uncertainty; never fabricate
  timestamps or shift spans to visually hide skew. Batch export delay is not span time.

## Deliverables And Definition Of Done

Deliver the smallest implementation/configuration/tests/docs consistent with the
existing project, plus the completed coverage table. Report versions, provider
ownership, endpoints/auth model, log enrichment, metrics and dashboards/queries,
sampling/privacy decisions, overhead checks, exact validation results, remaining
gaps and rollback steps. Include the trace ID, matching log evidence, metric series,
and queue propagation example where tested, without exposing sensitive payloads.

Do not mark the work complete solely because the app builds, the SDK starts, or an
OTLP endpoint returns 200. Distinguish implemented, exported, stored, correlated,
and unverified behavior. Never claim all logs become span events, all errors retain
traces, or metrics are correlated by adding trace IDs as metric labels.