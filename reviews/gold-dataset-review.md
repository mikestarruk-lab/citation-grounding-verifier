# Gold dataset review

Generated from dev.jsonl, test.jsonl and manifest.json. Edit those sources, then regenerate.
This document does not approve annotations or freeze the test split.
Review each fact's meaning, qualifiers, verdict, explanation and complete evidence chain.

| Split | Cases | Gold facts | S / C / U | Review status |
|---|---:|---:|---|---|
| dev | 8 | 12 | 8 / 2 / 2 | approved |
| test | 20 | 32 | 19 / 7 / 6 | draft |

## Source versions

- dev canonical dataset hash: `e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c`
- test canonical dataset hash: `19b9766741e3843a8deaea65dd7bef7bacc997eaf841dd7dd3afee338dbeb8e6`

### Full approval manifest

```json
{
  "version": 1,
  "dev": {
    "review_status": "approved",
    "reviewed_by": "Michael (mikestarruk-lab)",
    "reviewed_on": "2026-10-16",
    "dataset_hash": "e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c",
    "approval_record": "reviews/dev-gold-approval-2026-10-16.md"
  },
  "test": {
    "review_status": "draft",
    "reviewed_by": null,
    "frozen": false,
    "dataset_hash": null
  },
  "note": "Dev gold and v2 development outputs are owner-reviewed; see reviews/dev-v2/dev-v2-human-review-import-2026-10-17.json. Test gold remains pending. Owner review followed AI feedback and is not independent external validation."
}
```

## dev

### dev-01

```json
{
  "id": "dev-01",
  "source_group": "dev-archive",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days.
```

**generated_answer**

```text
ArchiveBox creates hourly snapshots. It retains snapshots for seven days.
```

#### g1 — SUPPORTED

**claim_text:** ArchiveBox creates a snapshot every hour.

**reasoning:** The source says ArchiveBox creates a snapshot every hour, which is equivalent to hourly snapshots.

**annotation_reason:** Keep snapshot frequency separate from retention duration; hourly is a valid paraphrase of every hour.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** ArchiveBox retains snapshots for seven days.

**reasoning:** The source explicitly retains ArchiveBox snapshots for seven days.

**annotation_reason:** The second answer sentence refers to ArchiveBox snapshots; retain the object and seven-day duration.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days."
  }
]
```


### dev-02

```json
{
  "id": "dev-02",
  "source_group": "dev-proxy",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
RelayGate retries GET requests after a connection reset. It never retries POST requests.
```

**generated_answer**

```text
RelayGate retries GET requests after a connection reset, but never retries POST requests.
```

#### g1 — SUPPORTED

**claim_text:** RelayGate retries GET requests after a connection reset.

**reasoning:** The source explicitly retries GET requests after a connection reset, matching the answer's request type and condition.

**annotation_reason:** The connection-reset condition is part of the fact; this does not establish retries after every kind of failure.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "RelayGate retries GET requests after a connection reset. It never retries POST requests."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** RelayGate never retries POST requests.

**reasoning:** The source states that RelayGate never retries POST requests.

**annotation_reason:** Resolve It to RelayGate and preserve never; the exception for POST is independent of the supported GET behavior.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "RelayGate retries GET requests after a connection reset. It never retries POST requests."
  }
]
```


### dev-03

```json
{
  "id": "dev-03",
  "source_group": "dev-worker",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
TaskDock permits at most four active workers. Additional workers remain queued.
```

**generated_answer**

```text
TaskDock permits five active workers. Additional workers remain queued.
```

#### g1 — CONTRADICTED

**claim_text:** TaskDock permits five active workers.

**reasoning:** The specification permits at most four active TaskDock workers, so permitting five active workers exceeds the stated maximum.

**annotation_reason:** Four is an inclusive upper bound on active workers, not a lower bound or a limit on queued workers.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "TaskDock permits at most four active workers. Additional workers remain queued."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** Additional TaskDock workers remain queued.

**reasoning:** The specification explicitly states that additional workers remain queued.

**annotation_reason:** Additional workers refers to workers beyond TaskDock's active-worker limit; this remains supported despite the answer's incorrect number.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "TaskDock permits at most four active workers. Additional workers remain queued."
  }
]
```


### dev-04

```json
{
  "id": "dev-04",
  "source_group": "dev-cache-negation",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
CedarCache does not persist entries across restarts.
```

**generated_answer**

```text
CedarCache persists entries across restarts.
```

#### g1 — CONTRADICTED

**claim_text:** CedarCache persists entries across restarts.

**reasoning:** The source says CedarCache does not persist entries across restarts, directly opposing the answer's persistence claim.

**annotation_reason:** Compare the same cache, entries, and restart condition; the answer reverses an explicit negation.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "CedarCache does not persist entries across restarts."
  }
]
```


### dev-05

```json
{
  "id": "dev-05",
  "source_group": "dev-durability",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
CachePebble writes entries to a local file after each update.
```

**generated_answer**

```text
CachePebble writes entries to a local file after each update. Its files are encrypted with AES-256.
```

#### g1 — SUPPORTED

**claim_text:** CachePebble writes entries to a local file after each update.

**reasoning:** The source explicitly writes CachePebble entries to a local file after each update.

**annotation_reason:** Preserve the after-each-update condition; the separate encryption assertion has a different evidential status.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "CachePebble writes entries to a local file after each update."
  }
]
```

#### g2 — UNSUPPORTED

**claim_text:** CachePebble files are encrypted with AES-256.

**reasoning:** The source describes local file writes but gives no encryption algorithm or encryption guarantee.

**annotation_reason:** Local storage neither establishes nor rules out AES-256; absence of evidence is not a contradiction.

**citations (original indices and verbatim quotes):**

```json
[]
```


### dev-06

```json
{
  "id": "dev-06",
  "source_group": "dev-protocol",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
WireFin reuses an established connection for subsequent requests.
```

**generated_answer**

```text
WireFin uses Brotli compression for request payloads.
```

#### g1 — UNSUPPORTED

**claim_text:** WireFin uses Brotli compression for request payloads.

**reasoning:** The only supplied behavior is connection reuse; the source does not specify request compression or Brotli.

**annotation_reason:** Connection reuse and payload compression are independent properties, so neither support nor direct refutation is available.

**citations (original indices and verbatim quotes):**

```json
[]
```


### dev-07

```json
{
  "id": "dev-07",
  "source_group": "dev-mode",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
Service Juniper runs in mode Q.
```

**context_passages[1]**

```text
Every service in mode Q encrypts its stored payloads.
```

**generated_answer**

```text
Service Juniper encrypts its stored payloads.
```

#### g1 — SUPPORTED

**claim_text:** Service Juniper encrypts its stored payloads.

**reasoning:** Passage 0 places Juniper in mode Q; passage 1 says every service in Q encrypts stored payloads. Together they entail the claim.

**annotation_reason:** Both the service's membership and the universal encryption rule are necessary; citing either passage alone omits a premise.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "Service Juniper runs in mode Q."
  },
  {
    "index": 1,
    "quote": "Every service in mode Q encrypts its stored payloads."
  }
]
```


### dev-08

```json
{
  "id": "dev-08",
  "source_group": "dev-host-location",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
The recovery worker runs on host Maple.
```

**context_passages[1]**

```text
Host Maple is located in region West.
```

**generated_answer**

```text
The recovery worker runs in region West.
```

#### g1 — SUPPORTED

**claim_text:** The recovery worker runs in region West.

**reasoning:** The worker runs on Maple according to passage 0, and Maple is in West according to passage 1, placing the worker in West.

**annotation_reason:** The conclusion follows by joining the same host Maple across the two passages; both location premises are required.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "The recovery worker runs on host Maple."
  },
  {
    "index": 1,
    "quote": "Host Maple is located in region West."
  }
]
```


## test

### test-01

```json
{
  "id": "test-01",
  "source_group": "test-upload",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
UploadPort accepts files up to and including 8 MiB. Larger files are rejected.
```

**generated_answer**

```text
UploadPort accepts an 8 MiB file and rejects larger files.
```

#### g1 — SUPPORTED

**claim_text:** UploadPort accepts an 8 MiB file.

**reasoning:** The specification accepts files up to and including 8 MiB, so a file exactly 8 MiB is accepted.

**annotation_reason:** Preserve the inclusive boundary; up to and including differs from strictly less than 8 MiB.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "UploadPort accepts files up to and including 8 MiB. Larger files are rejected."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** UploadPort rejects files larger than 8 MiB.

**reasoning:** The source rejects larger files, referring to files above its stated 8 MiB acceptance limit.

**annotation_reason:** The quotation retains the preceding threshold so Larger files has an explicit comparison value.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "UploadPort accepts files up to and including 8 MiB. Larger files are rejected."
  }
]
```


### test-02

```json
{
  "id": "test-02",
  "source_group": "test-session",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
A session expires after 15 minutes without activity. Activity resets the inactivity timer.
```

**generated_answer**

```text
Sessions expire after 15 inactive minutes. Activity resets the inactivity timer.
```

#### g1 — SUPPORTED

**claim_text:** Sessions expire after 15 minutes without activity.

**reasoning:** The source expires a session after 15 minutes without activity, matching 15 inactive minutes.

**annotation_reason:** Inactivity is a necessary qualifier; the source does not say every session expires 15 minutes after creation.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "A session expires after 15 minutes without activity. Activity resets the inactivity timer."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** Activity resets the inactivity timer.

**reasoning:** The source explicitly states that activity resets the inactivity timer.

**annotation_reason:** Timer reset is independently testable from the expiration interval and should remain a separate fact.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "A session expires after 15 minutes without activity. Activity resets the inactivity timer."
  }
]
```


### test-03

```json
{
  "id": "test-03",
  "source_group": "test-compression",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
When compact mode is enabled, IrisStore compresses newly written segments. Existing segments are unchanged.
```

**generated_answer**

```text
With compact mode enabled, IrisStore compresses newly written segments but leaves existing segments unchanged.
```

#### g1 — SUPPORTED

**claim_text:** When compact mode is enabled, IrisStore compresses newly written segments.

**reasoning:** The specification compresses newly written IrisStore segments when compact mode is enabled, exactly matching the qualified claim.

**annotation_reason:** Retain both the enabled-mode condition and the restriction to newly written segments.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "When compact mode is enabled, IrisStore compresses newly written segments. Existing segments are unchanged."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** With compact mode enabled, IrisStore leaves existing segments unchanged.

**reasoning:** In the compact-mode operation described by the source, existing IrisStore segments remain unchanged.

**annotation_reason:** Do not extend the compression rule from newly written to existing segments; keep the compact-mode scope.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "When compact mode is enabled, IrisStore compresses newly written segments. Existing segments are unchanged."
  }
]
```


### test-04

```json
{
  "id": "test-04",
  "source_group": "test-priority",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
BirchQueue processes high-priority messages before normal-priority messages. Messages within one priority are processed in arrival order.
```

**generated_answer**

```text
BirchQueue processes high-priority messages before normal-priority messages and uses arrival order within a priority.
```

#### g1 — SUPPORTED

**claim_text:** BirchQueue processes high-priority messages before normal-priority messages.

**reasoning:** The specification processes high-priority messages before normal-priority messages, exactly matching the claim.

**annotation_reason:** Keep the comparison relative to normal-priority messages, as the source states, without adding a priority class not mentioned there.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "BirchQueue processes high-priority messages before normal-priority messages. Messages within one priority are processed in arrival order."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** BirchQueue processes messages within a priority in arrival order.

**reasoning:** Within a single priority, the specification processes messages in arrival order.

**annotation_reason:** The ordering guarantee applies within one priority; it does not override the separate cross-priority rule.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "BirchQueue processes high-priority messages before normal-priority messages. Messages within one priority are processed in arrival order."
  }
]
```


### test-05

```json
{
  "id": "test-05",
  "source_group": "test-endpoint",
  "category": "supported",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
GET /status returns HTTP 200 with a JSON body. This endpoint requires no authentication.
```

**generated_answer**

```text
GET /status returns HTTP 200 and a JSON body without requiring authentication.
```

#### g1 — SUPPORTED

**claim_text:** GET /status returns HTTP 200.

**reasoning:** The first source sentence explicitly states that GET /status returns HTTP 200.

**annotation_reason:** Status code and response-body format are independently testable; this fact covers only the status code.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "GET /status returns HTTP 200 with a JSON body."
  }
]
```

#### g3 — SUPPORTED

**claim_text:** GET /status returns a JSON body.

**reasoning:** The first source sentence explicitly states that GET /status returns a JSON body.

**annotation_reason:** Separate body format from status code so a correct fine-grained prediction is not penalized as a duplicate.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "GET /status returns HTTP 200 with a JSON body."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** GET /status requires no authentication.

**reasoning:** The source states that this endpoint requires no authentication; the endpoint is GET /status in the preceding sentence.

**annotation_reason:** Preserve the existing authentication claim ID and retain enough quotation to resolve This endpoint.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "GET /status returns HTTP 200 with a JSON body. This endpoint requires no authentication."
  }
]
```


### test-06

```json
{
  "id": "test-06",
  "source_group": "test-retention",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
MeadowLog retains audit records for exactly 30 days and then deletes them.
```

**generated_answer**

```text
MeadowLog retains audit records for exactly 31 days.
```

#### g1 — CONTRADICTED

**claim_text:** MeadowLog retains audit records for exactly 31 days.

**reasoning:** The source retains audit records for exactly 30 days and then deletes them; exactly 31 days is incompatible with that duration.

**annotation_reason:** Exactly fixes the duration, and deletion rules out treating 30 days as merely a minimum retention period.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "MeadowLog retains audit records for exactly 30 days and then deletes them."
  }
]
```


### test-07

```json
{
  "id": "test-07",
  "source_group": "test-readonly",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
In read-only mode, PineDB rejects all writes. In read-write mode, it accepts writes.
```

**generated_answer**

```text
PineDB accepts writes in read-only mode.
```

#### g1 — CONTRADICTED

**claim_text:** PineDB accepts writes in read-only mode.

**reasoning:** In read-only mode the specification rejects all writes, directly refuting acceptance of writes in that same mode.

**annotation_reason:** The permission in read-write mode cannot be transferred to read-only mode; match the condition before comparing behavior.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "In read-only mode, PineDB rejects all writes. In read-write mode, it accepts writes."
  }
]
```


### test-08

```json
{
  "id": "test-08",
  "source_group": "test-deletion",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
Deleting a RiverLink project does not delete its exported files.
```

**generated_answer**

```text
Deleting a RiverLink project deletes its exported files.
```

#### g1 — CONTRADICTED

**claim_text:** Deleting a RiverLink project deletes its exported files.

**reasoning:** The specification says deleting a RiverLink project does not delete its exported files, the opposite of the claim.

**annotation_reason:** The same deletion operation and exported files appear in both statements; this is an explicit negation reversal.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "Deleting a RiverLink project does not delete its exported files."
  }
]
```


### test-09

```json
{
  "id": "test-09",
  "source_group": "test-replication",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
SableRep acknowledges a write only after both replicas confirm receipt. A single replica's confirmation is insufficient.
```

**generated_answer**

```text
SableRep acknowledges a write as soon as one replica confirms receipt.
```

#### g1 — CONTRADICTED

**claim_text:** SableRep acknowledges a write as soon as one replica confirms receipt.

**reasoning:** The specification waits for both replicas and explicitly says one confirmation is insufficient; acknowledging after just one contradicts it.

**annotation_reason:** Both confirmations are necessary, so a single confirmation cannot satisfy the acknowledgment condition.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "SableRep acknowledges a write only after both replicas confirm receipt. A single replica's confirmation is insufficient."
  }
]
```


### test-10

```json
{
  "id": "test-10",
  "source_group": "test-backup-default",
  "category": "distortion",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
Automatic backups are disabled by default in MossVault. Operators can enable them.
```

**generated_answer**

```text
MossVault enables automatic backups by default, and operators can enable them.
```

#### g1 — CONTRADICTED

**claim_text:** MossVault enables automatic backups by default.

**reasoning:** Automatic backups are disabled by default in the source, directly opposing enabled by default.

**annotation_reason:** Compare the default state independently of an operator's ability to change that state.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "Automatic backups are disabled by default in MossVault. Operators can enable them."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** Operators can enable automatic backups in MossVault.

**reasoning:** The specification explicitly allows operators to enable automatic MossVault backups.

**annotation_reason:** Manual enablement is supported even though the answer's separate assertion about the default state is contradicted.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "Automatic backups are disabled by default in MossVault. Operators can enable them."
  }
]
```


### test-11

```json
{
  "id": "test-11",
  "source_group": "test-index",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
FlintIndex indexes document titles. Body text is not indexed.
```

**generated_answer**

```text
FlintIndex indexes document titles and uses a B-tree internally.
```

#### g1 — SUPPORTED

**claim_text:** FlintIndex indexes document titles.

**reasoning:** The source explicitly states that FlintIndex indexes document titles.

**annotation_reason:** The answer asserts title indexing; do not add an extra answer claim just because the source also discusses body text.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "FlintIndex indexes document titles. Body text is not indexed."
  }
]
```

#### g2 — UNSUPPORTED

**claim_text:** FlintIndex uses a B-tree internally.

**reasoning:** The source identifies which document fields are indexed but does not describe the internal data structure.

**annotation_reason:** Title indexing does not entail a B-tree implementation, and no alternative structure is specified to refute it.

**citations (original indices and verbatim quotes):**

```json
[]
```


### test-12

```json
{
  "id": "test-12",
  "source_group": "test-metrics",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
MetricHarbor exposes a counter of completed jobs.
```

**generated_answer**

```text
MetricHarbor uses port 9090 for its metrics endpoint.
```

#### g1 — UNSUPPORTED

**claim_text:** MetricHarbor uses port 9090 for its metrics endpoint.

**reasoning:** The source describes a completed-jobs counter but gives no port number or metrics endpoint address.

**annotation_reason:** Do not supply port 9090 from conventions or external knowledge; no direct refutation is given either.

**citations (original indices and verbatim quotes):**

```json
[]
```


### test-13

```json
{
  "id": "test-13",
  "source_group": "test-timezones",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
ClockFern stores timestamps in UTC.
```

**generated_answer**

```text
ClockFern stores timestamps in UTC and synchronizes clocks using NTP.
```

#### g1 — SUPPORTED

**claim_text:** ClockFern stores timestamps in UTC.

**reasoning:** The specification explicitly stores ClockFern timestamps in UTC.

**annotation_reason:** Timestamp storage format is a separate property from the mechanism used to synchronize clocks.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "ClockFern stores timestamps in UTC."
  }
]
```

#### g2 — UNSUPPORTED

**claim_text:** ClockFern synchronizes clocks using NTP.

**reasoning:** The source specifies UTC timestamp storage but never mentions NTP or a clock-synchronization mechanism.

**annotation_reason:** UTC does not establish NTP use; the missing mechanism makes this unsupported rather than contradicted.

**citations (original indices and verbatim quotes):**

```json
[]
```


### test-14

```json
{
  "id": "test-14",
  "source_group": "test-container",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
SpruceRunner launches each job in an isolated container.
```

**generated_answer**

```text
SpruceRunner schedules its containers using Kubernetes.
```

#### g1 — UNSUPPORTED

**claim_text:** SpruceRunner schedules its containers using Kubernetes.

**reasoning:** The source specifies an isolated container for each job but does not identify its scheduler or orchestrator.

**annotation_reason:** Container isolation alone does not imply Kubernetes, and the source provides no contrary orchestration choice.

**citations (original indices and verbatim quotes):**

```json
[]
```


### test-15

```json
{
  "id": "test-15",
  "source_group": "test-licensing",
  "category": "extrinsic",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
QuartzCLI includes export and import commands.
```

**generated_answer**

```text
QuartzCLI includes export commands and is distributed under the Apache 2.0 license.
```

#### g1 — SUPPORTED

**claim_text:** QuartzCLI includes export commands.

**reasoning:** The specification includes both export and import commands, which entails the answer's export-command claim.

**annotation_reason:** A claim about export does not need to repeat every source capability; do not manufacture an omitted import claim.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "QuartzCLI includes export and import commands."
  }
]
```

#### g2 — UNSUPPORTED

**claim_text:** QuartzCLI is distributed under the Apache 2.0 license.

**reasoning:** The source describes commands but provides no distribution license.

**annotation_reason:** Command availability does not establish Apache 2.0 licensing; no alternative license is stated to contradict it.

**citations (original indices and verbatim quotes):**

```json
[]
```


### test-16

```json
{
  "id": "test-16",
  "source_group": "test-archive-chain",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
The Acorn project uses the bronze retention policy.
```

**context_passages[1]**

```text
Under the bronze policy, archived objects are retained for 90 days.
```

**generated_answer**

```text
Archived objects in the Acorn project are retained for 90 days.
```

#### g1 — SUPPORTED

**claim_text:** Archived objects in the Acorn project are retained for 90 days.

**reasoning:** Passage 0 assigns Acorn the bronze policy; passage 1 retains archived objects under bronze for 90 days. The duration therefore applies to Acorn's archived objects.

**annotation_reason:** Join the same bronze policy across both passages and preserve the archived-object scope and 90-day duration.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "The Acorn project uses the bronze retention policy."
  },
  {
    "index": 1,
    "quote": "Under the bronze policy, archived objects are retained for 90 days."
  }
]
```


### test-17

```json
{
  "id": "test-17",
  "source_group": "test-authorization-chain",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
User Lina has the auditor role.
```

**context_passages[1]**

```text
Auditors can view logs but cannot delete logs.
```

**generated_answer**

```text
Lina can view logs. Lina can delete logs.
```

#### g1 — SUPPORTED

**claim_text:** Lina can view logs.

**reasoning:** Lina has the auditor role, and the role rule permits auditors to view logs, so Lina can view logs.

**annotation_reason:** Both role assignment and the permission rule are required; do not infer additional roles or overrides.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "User Lina has the auditor role."
  },
  {
    "index": 1,
    "quote": "Auditors can view logs but cannot delete logs."
  }
]
```

#### g2 — CONTRADICTED

**claim_text:** Lina can delete logs.

**reasoning:** Lina is an auditor, and auditors cannot delete logs, directly refuting Lina's claimed deletion permission.

**annotation_reason:** The contradiction needs both passages: the role assignment connects Lina to the explicit deletion prohibition.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "User Lina has the auditor role."
  },
  {
    "index": 1,
    "quote": "Auditors can view logs but cannot delete logs."
  }
]
```


### test-18

```json
{
  "id": "test-18",
  "source_group": "test-missing-condition",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
Service Finch uses engine Ember. Finch's engine configuration is not specified here.
```

**context_passages[1]**

```text
Engine Ember encrypts writes when secure mode is enabled.
```

**generated_answer**

```text
Service Finch encrypts writes.
```

#### g1 — UNSUPPORTED

**claim_text:** Service Finch encrypts writes.

**reasoning:** Finch uses Ember. The source guarantees encrypted writes when secure mode is enabled, but does not establish that this condition holds for Finch or otherwise establish encryption. It also does not refute encryption, so the claim is unsupported.

**annotation_reason:** An unspecified secure-mode setting proves neither encryption nor its absence; do not turn this missing condition into a contradiction.

**citations (original indices and verbatim quotes):**

```json
[]
```


### test-19

```json
{
  "id": "test-19",
  "source_group": "test-arithmetic",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
The shared request pool has exactly 12 slots.
```

**context_passages[1]**

```text
Seven slots are occupied. Every slot is either occupied or available.
```

**generated_answer**

```text
The shared request pool has five available slots.
```

#### g1 — SUPPORTED

**claim_text:** The shared request pool has five available slots.

**reasoning:** There are exactly 12 slots and seven are occupied. With occupied and available as the two states, the remaining 12 minus 7 equals five available slots.

**annotation_reason:** Both the total and the occupied/available state partition are needed for the arithmetic; keep both passages as evidence.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "The shared request pool has exactly 12 slots."
  },
  {
    "index": 1,
    "quote": "Seven slots are occupied. Every slot is either occupied or available."
  }
]
```


### test-20

```json
{
  "id": "test-20",
  "source_group": "test-release-routing",
  "category": "multi_passage",
  "provenance": "Synthetic specification authored for this assignment; not a claim about a real product."
}
```

**context_passages[0]**

```text
Production traffic is routed exclusively to release Azure.
```

**context_passages[1]**

```text
Release Azure rejects protocol V1 and accepts protocol V2.
```

**generated_answer**

```text
Production accepts protocol V1 and protocol V2.
```

#### g1 — CONTRADICTED

**claim_text:** Production accepts protocol V1.

**reasoning:** Production routes exclusively to Azure, which rejects V1. Production therefore cannot accept V1 under the supplied routing rule.

**annotation_reason:** The rejection must be linked to production through the exclusive Azure route; either passage alone leaves that link unproved.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "Production traffic is routed exclusively to release Azure."
  },
  {
    "index": 1,
    "quote": "Release Azure rejects protocol V1 and accepts protocol V2."
  }
]
```

#### g2 — SUPPORTED

**claim_text:** Production accepts protocol V2.

**reasoning:** Production routes exclusively to Azure, and Azure accepts V2, supporting production's acceptance of V2.

**annotation_reason:** Combine the routing premise with the V2 acceptance rule without introducing other releases or routing exceptions.

**citations (original indices and verbatim quotes):**

```json
[
  {
    "index": 0,
    "quote": "Production traffic is routed exclusively to release Azure."
  },
  {
    "index": 1,
    "quote": "Release Azure rejects protocol V1 and accepts protocol V2."
  }
]
```
