# Traces, Logs, Metrics, And Correlation

## Do Not Confuse The Signals

- A span describes a bounded operation; a trace is the related span graph.
- A structured log describes an event and can carry the active `TraceId`, `SpanId`
  and `TraceFlags`. It is stored/exported independently from spans.
- A metric aggregates observations over time. Common resource/operation dimensions
  connect charts to services; exemplars can connect individual observations to a
  trace. Do not put trace/span/request/user/message IDs into metric labels.
- A log containing matching IDs is correlated with a span, not automatically stored
  inside it. Span events are separate annotations; a log bridge does not necessarily
  create them. Configure the backend's trace-to-logs lookup and metric exemplar links.

## Extend Existing Logs

1. Identify the existing logger and sinks: .NET ILogger/Serilog/NLog, Java
   SLF4J/Logback/Log4j, Node Pino/Winston, Python logging/structlog, Go slog/zap or
   another framework. Verify its maintained OTel bridge and compatible versions.
2. Choose one ingestion path per log stream: direct OTel logging exporter, or
   structured stdout/file plus a Collector/agent that parses/maps the record.
   Do not export the same log through both paths without an intentional dedup policy.
3. Enrich at emission time from the active operation context, before async queues
   discard thread/request scope. An async transport cannot safely look up whatever
   request happens to be active when it eventually exports the record.
4. Populate the OTel context fields, not only a printable `trace_id` string in the
   body. For JSON/stdout bridges map source correlation fields into OTel TraceId,
   SpanId and flags explicitly, preserving structured attributes.
5. Startup/background logs outside a valid span legitimately lack context. Do not
   attach them to the last request or invent random trace IDs for every log.
6. Preserve event/observed timestamps, severity number/text, stable event name or
   message template, body, resource and instrumentation scope. Keep original error
   classification when redacting messages; errors are not all application crashes.
7. Add approved bounded attributes: operation/route template, result/outcome,
   dependency type, error class/code, retry attempt and safe deployment metadata.
   Business/correlation IDs need explicit approval and retention; exclude them
   from metrics and indexing labels even if permitted as log attributes.
8. Log failed operations with safe exception type/stack and meaningful severity.
   Preserve default framework error handlers and rethrow behavior. Avoid one
   exception being logged at every layer or by multiple competing crash handlers.
9. Redact before SDK buffers, console/file persistence, or durable crash spools as
   required by policy; an exporter-only filter protects export, not earlier storage.
   Recheck bodies, attributes, resources, scope attributes, events, links and stack
   frames. Prefer allowlists; regex-only cleanup is not a complete privacy strategy.
10. Ensure Collector transforms, storage mappings and queries preserve IDs and
    resources. Build a trace-ID lookup/derived-field link in Grafana/Loki or the
    selected backend; SDK configuration alone does not configure the UI.

Suggested logical record (use SDK types, not this JSON as an OTLP wire payload):

```json
{
  "timestamp": "<event-time>",
  "severity": "ERROR",
  "event.name": "dependency.operation.failed",
  "body": "Dependency operation failed",
  "service.name": "orders-api",
  "service.version": "<release>",
  "deployment.environment.name": "<environment>",
  "trace_id": "<active-trace-id>",
  "span_id": "<active-child-span-id>",
  "trace_flags": "<active-flags>",
  "operation": "reserve-inventory",
  "error.type": "TimeoutError"
}
```

The bridge maps these logical context fields to the actual OTel log fields. Never
hardcode example IDs. Verify correlation on exported and stored data, including a
log from an inner DB/broker operation and one after async execution resumes.

## Span Events And Error Recording

- Add small, bounded events for meaningful milestones: validation completed,
  fallback selected, transaction committed, or a safe exception event if supported.
  Use the selected exception conventions; do not duplicate a sensitive log body.
- If a requirement says "show logs inside the trace", clarify whether correlated
  logs in the UI, explicit span events, or both are required. Implement and test the
  requested representation instead of mirroring all logs indiscriminately.
- Keep span status and log severity independent. Expected validation failure or a
  handled fallback may warrant WARN without marking an entire request as failed.
- Always end spans in cleanup while preserving errors/cancellation. Record original
  failure category without adding private error text to status descriptions.
- Parent-based sampling does not guarantee a trace exists for every error log.
  For error retention, agree head sampling versus Collector tail sampling, routing
  of all spans to the tail sampler, trace completion windows and memory limits.
  Tail sampling cannot recover spans already dropped by head sampling.

## Application Metrics

Prefer SDK/client-provided standard metrics and current semantic conventions.
Use custom names only for missing domain measurements, with documented units and
ownership. Never assume that enabling traces also enables logs or metrics.

| Area | Measurements to consider | Safe grouping dimensions |
| --- | --- | --- |
| Inbound API | Request rate, errors, duration histogram, active requests | Service, method, route template, status class/code |
| Outbound HTTP/RPC | Calls, duration, errors/timeouts, retries, in-flight operations | Approved remote service/operation, method, bounded outcome |
| Database | Operation duration/errors, pool usage/wait/timeout, transaction outcome | DB system, approved namespace, operation/summary |
| Cache | Hits/misses, duration/errors, fallback/stale/invalidation | Cache identity, command family, bounded result |
| Messaging | Send/process rate, duration/errors, settlement, retries, in-flight work | System, approved topic/queue template, consumer group if bounded |
| Broker/system | Consumer lag, queue depth/age, throttling and availability | Approved infrastructure dimensions, sourced from broker/agent |
| Runtime | CPU, memory, GC, threads/event-loop, pool/worker saturation | Approved instance/deployment identity |
| Frontend/mobile | User-visible operation/startup duration, Web Vitals, error/crash rate | App version, route/screen template, bounded error category |
| Business | Accepted/rejected/completed work, pending/unknown outcomes, queue time | Operation/result classes, not individual entities |

- Use counters for cumulative occurrences, histograms for distributions, and
  gauges/up-down instruments for appropriate observed/in-flight state. Do not
  record one value into incompatible instruments simply to populate a dashboard.
- Choose duration units and latency buckets appropriate to the operation; document
  histogram temporality and aggregation. Check SDK-to-Prometheus name/unit conversion
  before writing queries; seconds in OTel may have a converted series name.
- Separate physical attempts from user/business operations. Do not double-count
  responses, retries, cancellation and finalization, or count an uncertain write as
  a confirmed failure/success. Restore active/in-flight gauges on every exit path.
- Record within the active context and enable trace-based exemplars when supported
  by SDK, export format, Collector, metric store and UI. Verify a chart exemplar
  resolves to a retained trace; missing exemplars can be expected with sampling.
- Metric collection is independent of trace sampling. Do not derive authoritative
  traffic/error rates only from sampled spans. If span/log-derived metrics are used,
  document their sampling/duplication assumptions, pipeline stage and denominator.
- Logs do not automatically become metrics. Prefer counters at the operation/error
  boundary. If log-to-metric rules are required, define them explicitly at one
  ingestion stage, prevent replay double-counting where feasible, and bound labels.
- Never use raw URLs, IDs, messages, SQL text, stack traces, Redis keys or individual
  tenant/user identifiers as metric dimensions. Estimate and enforce a series budget.
- Common dimensions/resources connect services, not every timestamp or operation:
  request-level navigation requires exemplars or a log/trace query, not aggregate
  metric equality. Metrics can arrive on different export/scrape intervals.

## Export And Reliability Contract

- Verify a complete path for each signal: SDK/bridge -> proxy/gateway -> Collector
  receiver -> processor -> exporter -> storage -> query/UI. Do not confuse acceptance
  by one hop with end-to-end retention or exactly-once delivery.
- Keep resources and correlation intact while redacting. Do not replace the full
  resource with a partial allowlist without preserving approved SDK/runtime/service
  metadata and testing the backend identity impact.
- Custom projections must preserve getter-backed metadata explicitly: timestamps,
  observed timestamps, span context, scope, status, parent context, units and counts
  as applicable. Object spreading can omit SDK getters. Test actual OTLP serialization
  and stored results in addition to in-memory exporter snapshots.
- Bound queues, batch sizes, attempts, timeouts, disk retention and shutdown wait.
  Failed crash export can retain a bounded sanitized spool for restart replay.
  Processor `forceFlush` success is not necessarily a delivery acknowledgement.
- Configure SDK-internal diagnostics separately to avoid telemetry recursion. Track
  Collector queue pressure, refused/dropped data and exporter errors via a separate
  approved monitoring path. Do not claim failure-free export during a backend outage.

## Required Correlation Checks

1. Capture a real HTTP request or message header and compare it with the emitted
   client/producer context and downstream parent IDs or links; flags can contain
   valid bits beyond the sampled flag, so do not require literal `01` blindly.
2. Emit a structured log inside a known active span; verify exact IDs, severity,
   timestamps and service identity on the wire and in storage, and open it from the
   trace UI. Test two concurrent operations and no-span startup logs.
3. Exercise a success, error, timeout and retry; verify appropriate metric deltas and
   histogram observations, safe dimensions, and exemplars where enabled.
4. Use synthetic secret/PII markers in errors and dependency inputs; assert that they
   are absent from exported payloads, approved persistence and indexed labels.
5. Test framework errors, real browser event delivery, mobile crash/restart and
   Collector outage where relevant. Explicitly dispatched events do not prove the
   runtime generates those events; report actual verification coverage.

## Official References

- [Logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [Log SDK and context](https://opentelemetry.io/docs/specs/otel/logs/sdk/)
- [Metrics data model and exemplars](https://opentelemetry.io/docs/specs/otel/metrics/data-model/)
- [Semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
- [Collector configuration](https://opentelemetry.io/docs/collector/configuration/)