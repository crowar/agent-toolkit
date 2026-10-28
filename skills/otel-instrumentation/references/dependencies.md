# Dependency Instrumentation Rules

Read this for each dependency actually used by the application. Discover concrete
client libraries, versions, pooling, wrappers, proxy layers, and asynchronous APIs.
Use maintained instrumentation compatible with those versions; do not guess package
names or enable every integration shipped by an agent.

## Coverage Matrix

| Dependency | Required application visibility | Additional system visibility |
| --- | --- | --- |
| Microsoft SQL Server / MSSQL | SqlClient/JDBC/ODBC or actual driver calls, stored procedures, timeouts, transactions | Pool pressure, connections, locks, deadlocks, query performance from approved DB monitoring |
| PostgreSQL | Npgsql/pg/psycopg/pgx or actual driver, ORM and raw SQL paths, commit/rollback | Connections/pool, lock waits, replication and server health from DB monitoring |
| Redis / Valkey | Actual Redis client, command duration/error, cache hit/miss, fallback/invalidation | Memory, evictions, connections, replication and server latency |
| MySQL, MariaDB, Oracle, SQLite | Compatible driver hooks, operation duration and transaction outcomes | Pool/server metrics as applicable; SQLite is not a remote server |
| MongoDB, DynamoDB, Cosmos DB, Cassandra | Collection/operation API, batch/pagination, timeout/throttling | Capacity, throughput, replication, storage and vendor metrics |
| Elasticsearch / OpenSearch | Search/index/bulk logical operations; avoid duplicate SDK + HTTP spans | Rejections, queue pressure, cluster/shard health |
| Kafka | Send/creation context, consume/process, commit/error, retries and batches | Consumer lag, broker/topic health, rebalance and throughput monitoring |
| RabbitMQ / AMQP | Publish confirmation, delivery/process, ack/nack/reject/requeue and DLQ | Queue depth/age, unacked messages, connections, broker health |
| External HTTP / gRPC / GraphQL / SOAP | Outbound call duration/status, cancellation/timeout, safe target identity | Remote internals only with that system's instrumentation/access |
| Object/blob storage, file/SFTP, email, third-party SDKs | Upload/download/read/write/send boundaries and outcomes | Provider service metrics, quotas and availability |
| Jobs, schedulers, workflows, webhooks, WebSocket/streams | Enqueue/run/context handoff, completion/failure, per-operation spans | Queue age, scheduling delay, backlog and worker utilization |

Application instrumentation does not automatically expose broker/DB internals.
Use existing Collector receivers, Prometheus exporters, cloud integrations or
operator-approved infrastructure agents for those metrics. They require separate
credentials/permissions and do not make remote internals child spans automatically.

## SQL, NoSQL, And Cache

1. Instrument the real driver or supported higher-level API. In .NET inspect the
   actual SqlClient, Npgsql, EF Core and Redis integrations; in Java inspect agent,
   JDBC/ORM/client hooks; in Node, Python and Go verify the concrete client/import
   versions and async support. Framework support alone does not cover every driver.
2. Prefer the caller's logical database operation, including retries internal to the
   driver according to its conventions. Do not emit identical spans from agent,
   driver, ORM and manual wrappers. Distinct domain/transaction spans are useful
   only when their responsibilities and parent/child boundaries are documented.
3. Preserve selected semantic-convention keys such as `db.system.name`,
   `db.namespace`, `db.operation.name`, `db.query.summary`, `server.address`, and
   `server.port` where supported. Existing integrations may use older names;
   migrate schema intentionally with dashboard/query compatibility tests.
4. Use static operation summaries/allowlisted collection names. Query text is not
   mandatory for this skill. Prefer summaries; collect approved parameterized or
   dialect-aware sanitized statements only under the data policy. Never capture
   bind parameter values, interpolated literals, SQL comments containing user data,
   Redis keys/values, documents, result sets, connection strings or credentials.
   Do not invent SQL sanitization by a few regex substitutions; omit unsafe text.
5. Keep SQL parameterization and transaction semantics unchanged. Capture a failed
   commit, rollback, timeout or pool acquisition separately from successful query
   execution; never report the whole transaction successful before commit.
6. Separate application pool wait, query duration, transaction duration, and
   observable connection usage if hooks exist. Use driver/DB metrics when waits or
   locks are not visible from instrumentation; label unavailable measurements as gaps.
7. For Redis distinguish cache hit, miss, bypass, stale response, invalidation,
   fallback-to-database and unavailable cache using bounded outcomes. Count a miss
   only when a lookup actually occurred. Do not turn an expected miss into an error.
8. Pipelines/bulk APIs should follow client semantics with bounded operation counts,
   not unlimited spans per key/row. Multi-key requests are not necessarily batches.
9. Do not inject W3C HTTP headers into SQL or Redis commands. SQL commenter is an
   explicit, approved opt-in only: comments may leak context or change query/plan
   cache behavior, especially with prepared statements and SQL Server.

## Kafka, RabbitMQ, And Other Messaging Systems

Follow the semantic-convention version implemented by the chosen library.
Messaging conventions evolve; do not silently rewrite a running integration to
the newest names or force every producer/consumer into one parent-child trace.

### Context And Span Boundaries

- Propagate a message creation context through supported message headers/properties
  using the SDK propagator. Kafka headers can be byte arrays and RabbitMQ headers
  can be typed values; use supported adapters and test encoding/decoding.
- A single-message send can use its PRODUCER span as creation context. A batch may
  use per-message creation spans or a documented shared creation context. Preserve
  context supplied by an existing instrumentation owner instead of overwriting it.
- Current messaging conventions default to links from receive/process spans to
  each message's creation context. A single-message process MAY use that context
  as its parent if the integration documents this policy. With existing ambient
  HTTP/job context, retain the relevant relationships through links.
- A batch span cannot have multiple parents: use links for multiple messages. Put
  attributes that differ per message on appropriate links or child operations,
  not a misleading single message ID on a batch. Bound link/event counts.
- Distinguish create/send, pull receive, application process, and settle. Select
  kinds from the supported conventions: process is CONSUMER; pull receive/settle
  are CLIENT; send can be PRODUCER or CLIENT depending on creation-context ownership.
- Make processing context active around the handler, logs, DB calls and produced
  messages; restore it after each delivery. Test parallel consumers and executors.
- End send at actual delivery/confirmation completion as exposed by the client,
  not merely when a local enqueue method returns. Do not include broker queue time
  as active consumer processing. Distinguish delivery delay from handler duration.
- Record settlement failures, publish rejection, cancellation and redelivery with
  bounded outcome/error classes. Treat empty polls/prefetch according to library
  semantics, not as business messages or failures.

### Kafka-Specific Checks

- Verify context survives producer callbacks, interceptors, consumer polling,
  concurrent record handlers, batching, retries, rebalance and worker handoff.
- Observe commit success/failure separately from processing success. Do not change
  auto/manual commit, transactions, ordering, partition assignment or delivery
  guarantees to simplify traces. Rebalance/cancellation does not prove data loss.
- Measure application processing rate/duration/errors, in-flight work and retries.
  Collect consumer lag/partition offsets from approved client or broker metrics;
  a producer and consumer's wall clocks alone cannot establish reliable lag.

### RabbitMQ-Specific Checks

- Inspect the actual AMQP client, delivery callback and channel/pool lifecycle.
  Verify routing through exchanges, queues, forwarding and dead-letter paths.
- Publisher confirms and unroutable returns are not consumer acknowledgements.
  Preserve ack/nack/reject/requeue settings; record settlement where observable.
- Retries/DLQ republishing need an explicit causal policy: preserve original
  creation links, inject the current send context where appropriate, and create
  separate processing attempts. Never reuse one active span for multiple deliveries.
- Collect ready/unacked queue depth, message age, redelivery rate and publisher
  confirmation latency from suitable application/broker sources; do not guess.

For SQS/SNS, Azure Service Bus, Pub/Sub, Pulsar, NATS or other brokers, apply the
same creation-context, batch/link, delivery/processing/settlement, privacy and
validation rules, while preserving vendor-specific acknowledgement semantics.

## External HTTP, RPC, And Other Systems

- Use one CLIENT span per actual HTTP/RPC call as modeled by its instrumentation.
  Cover completion, body consumption/streaming policy, errors, timeout, DNS/TLS
  failures and cancellation. Separate user operation latency from attempt latency.
- Use route/operation templates and allowlisted remote service identity. Remove
  URL credentials, query strings, fragments, raw GraphQL documents/variables,
  SOAP envelopes, and headers with tokens, cookies or personal data.
- Inject context only into approved destinations. Gateways/proxies must preserve
  permitted headers; third parties may ignore them. Without remote instrumentation
  the client span still measures the call, not the provider's internal trace.
- Respect existing retries, hedging and circuit breakers. Distinct attempts can
  be child spans when supported; do not count one request as multiple successes or
  change non-idempotent requests because telemetry export retries are enabled.
- Use maintained SDK hooks for object stores/search/mail/cloud APIs. Avoid duplicate
  logical SDK and low-level HTTP spans unless the hierarchy adds documented meaning.
- Instrument WebSocket message operations and reconnects rather than treating an
  entire user session as one request. Propagate approved per-message metadata if
  the protocol supports it; streaming connections require explicit bounded spans.
- For detached work, persist/propagate a causal context and use links where lifetime
  differs from the request. Never keep a request artificially open until a delayed
  job completes, and never serialize a thread-local context object.

## Dependency Acceptance Checklist

- Trigger each real path with disposable/synthetic data, including ORM/raw-driver,
  cache hit/miss/fallback, external errors and transaction completion where present.
- Verify parent IDs or links, active log context, metric increments, no duplicated
  physical operations, and absence of SQL parameters/message bodies/secret headers.
- For messaging exercise publish -> receive/process -> DB/external call -> settle,
  plus batch, retry/redelivery, failed publish, parallel handling and shutdown.
- Preserve delivery semantics and prove missing/invalid context does not break work.
- Report application versus infrastructure metrics separately with their sources,
  permissions, dashboards and remaining coverage gaps.

## Official References

- [Database conventions](https://opentelemetry.io/docs/specs/semconv/database/)
- [Database spans](https://opentelemetry.io/docs/specs/semconv/database/database-spans/)
- [Messaging spans](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/)
- [HTTP conventions](https://opentelemetry.io/docs/specs/semconv/http/)
- [Instrumentation registry](https://opentelemetry.io/ecosystem/registry/)