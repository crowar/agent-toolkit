# Pitfalls And Local Verification

Lessons from real runs. Check each item before declaring telemetry "exported".

## Discover What Already Owns Each Signal

- Corporate/base logging packages often own part of the pipeline (for example a
  package that wires Serilog JSON stdout plus a tracer provider with a hardcoded
  OTLP protocol, sampler and instrumentations). Read the package README, nuspec
  and, if needed, its strings/IL before adding anything. Record per signal: owner,
  protocol, endpoint/headers source, sampler, resource attributes, level filters.
- Extend the existing provider (`AddOpenTelemetry().WithTracing/WithMetrics/WithLogging`
  is additive in .NET); never create a second provider for a signal already owned.
- Protocols must match across signals. If a library hardcodes gRPC for traces, use
  gRPC (`OTEL_EXPORTER_OTLP_PROTOCOL=grpc`, port 4317) for logs/metrics too, unless
  the split is intentional. Do not send HTTP/protobuf and gRPC to the same port.
- Verify an instrumentation source really exists before `AddSource`/`AddMeter`:
  some libraries use `DiagnosticListener` instead of `ActivitySource` (Quartz.NET
  needs `OpenTelemetry.Instrumentation.Quartz`; Npgsql has a native `Npgsql` source
  and meter). Add `AddMeter` for built-in meters that produce "will be ignored"
  SDK warnings (for example `Microsoft.AspNetCore.Routing`).

## Logs Through Serilog (.NET)

- `UseSerilog` replaces `ILoggerFactory`, so the OTel `ILoggerProvider` receives
  nothing. Bridge deliberately: a composite `ILoggerFactory` that forwards to both the
  original factory and the OTel provider, registered after the library's
  `ConfigureServices` (later registration wins). Fall back to the original factory
  when no OTel provider is registered (test hosts).
- Calling `OpenTelemetryLoggerProvider.CreateLogger` directly bypasses
  `Logging:LogLevel` filters, so Debug/Trace and noisy `Microsoft.*` categories leak
  into OTLP. Build the OTel side with `new LoggerFactory(providers, LoggerFilterOptions)`
  using the configured `IOptionsMonitor<LoggerFilterOptions>`. Verify by decoding or
  grepping exported payloads for severities that must be absent.
- Keep stdout output byte-identical; do not export the same stream through two paths.

## Runtime Environment Traps

- `launchSettings.json` `environmentVariables` override the shell for `dotnet run`
  and IDE launches. Run with `--no-launch-profile` when verifying, and inspect the
  profile for stale `OTEL_EXPORTER_OTLP_ENDPOINT` values (for example `localhost`).
- Run from the project directory so `appsettings*.json` is found.
- Bash: an assignment with a space in the value must use `env "VAR=value with space" cmd`;
  `'VAR=a b' cmd` is treated as a command name and the app silently never starts.
  Check the app really started before trusting an empty receiver log.
- .NET `HttpClient` ignores CIDR entries in `NO_PROXY` (`10.0.0.0/8`) while curl
  honours them. With `HTTP(S)_PROXY` set, OTLP gRPC to an internal IP goes through the
  proxy and fails with `Requesting HTTP version 2.0 ... unable to establish HTTP/2`
  or `PROTOCOL_ERROR`. Add the collector host/IP explicitly to `NO_PROXY`/`no_proxy`.
- Header values: `OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer <token>`. Pass the
  token through the environment/secret store only; never write it into code,
  launch settings, docs, commit messages or skill/session notes.
- A `localhost:<random port>` exporter URL in SDK diagnostics means something other
  than the intended config (IDE, test runner) injected the endpoint; find it.

## Local Verification Recipe

1. Probe the collector first with curl: no token -> 401; token -> 200 on `/v1/{logs,metrics,traces}`
   (HTTP, `Content-Type: application/x-protobuf`, empty body) and, for gRPC,
   `curl --http2-prior-knowledge` to the service path returns `HTTP/2 200` + `grpc-status`.
2. Run the app with `http/protobuf` against a throwaway local receiver (a small
   script logging path, size, severity counts) to prove each signal is emitted.
   Do not put a re-encoding proxy in front of a real collector: Python/other clients
   may get different status codes (403) than the app; replay the captured payload
   with curl instead.
3. SDK self-diagnostics: `OTEL_DIAGNOSTICS.json` is read from the application base
   directory (`bin/<cfg>/<tfm>/`), not the working directory; remove it afterwards.
   Use a deliberately wrong token as a negative control to confirm diagnostics work.
4. Confirm the established connection (`ss -tnp | grep <collector>`) and, in the
   backend UI, filter by `service.name`; remember batch export delay (traces ~5s,
   metrics = `OTEL_METRIC_EXPORT_INTERVAL`).
5. Run the existing tests before and after. If failures appear, separate them from
   unrelated uncommitted user changes (`git status`, stash only your own files)
   before reporting. Clean up temp scripts, diagnostics files and logs.

## Deliverable Addition

Always give the user one copy-paste launch command for a clean terminal containing
every required `OTEL_*`, proxy (`NO_PROXY`) and profile flag (`--no-launch-profile`),
with the token as a placeholder.
