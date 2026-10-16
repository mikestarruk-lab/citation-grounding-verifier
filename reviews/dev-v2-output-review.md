# Development v2 output review

Status: pending human review. Development gold is approved; model outputs are not.
Method names are hidden as A/B. Output style may still reveal the method.
Review this document before inspecting method-labelled experiment files.

For each prediction: align by factual meaning only, preserve all qualifiers,
and record the matching gold ID (or null). Judge evidence sufficiency for
SUPPORTED/CONTRADICTED predictions independently of citation legality.
Split compound predictions into faithful units retaining the original
prediction index, verdict and citations. Keep duplicates in original order.
Do not choose the better-labelled duplicate for credit.
Approve a packet only after all its predictions and missing facts are checked.

Dataset hash: `e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c`.

Reply using case ID, A/B, prediction index, gold ID and evidence sufficiency.
Example format: `dev-01 / A / prediction 0 -> g1; evidence sufficient: yes`.
Flag omissions and necessary splits explicitly. Review time is not measured
by generation timestamps; record actual reviewer time if available.

## dev-01

**Sources**

Passage 0

```text
ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days.
```

**Generated answer**

```text
ArchiveBox creates hourly snapshots. It retains snapshots for seven days.
```

**Approved gold**

```json
[
  {
    "claim_text": "ArchiveBox creates a snapshot every hour.",
    "verdict": "SUPPORTED",
    "reasoning": "The source says ArchiveBox creates a snapshot every hour, which is equivalent to hourly snapshots.",
    "citations": [
      {
        "index": 0,
        "quote": "ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days."
      }
    ],
    "id": "g1",
    "annotation_reason": "Keep snapshot frequency separate from retention duration; hourly is a valid paraphrase of every hour."
  },
  {
    "claim_text": "ArchiveBox retains snapshots for seven days.",
    "verdict": "SUPPORTED",
    "reasoning": "The source explicitly retains ArchiveBox snapshots for seven days.",
    "citations": [
      {
        "index": 0,
        "quote": "ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days."
      }
    ],
    "id": "g2",
    "annotation_reason": "The second answer sentence refers to ArchiveBox snapshots; retain the object and seven-day duration."
  }
]
```

### dev-01 / A

Review ID: `54375d9ba5082f3a`

Output hash: `b1416fb783e67787b8c42c0d14e2e003e5a2c63a9094afcfa2f24639c35a0fb7`

**Prediction 0**

```json
{
  "claim_text": "ArchiveBox creates hourly snapshots.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Prediction 1**

```json
{
  "claim_text": "It retains snapshots for seven days.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "ArchiveBox creates hourly snapshots.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "It retains snapshots for seven days.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-01 / B

Review ID: `a47bcd3a5048ceb0`

Output hash: `abe5197b71601efdbc3fee9d372eca3912ec43f6d569ad211cb04a1107795249`

**Prediction 0**

```json
{
  "claim_text": "ArchiveBox creates hourly snapshots.",
  "verdict": "SUPPORTED",
  "reasoning": "Passage 0 states that ArchiveBox creates a snapshot every hour.",
  "citations": [
    {
      "index": 0,
      "quote": "ArchiveBox creates a snapshot every hour."
    }
  ]
}
```

**Prediction 1**

```json
{
  "claim_text": "ArchiveBox retains snapshots for seven days.",
  "verdict": "SUPPORTED",
  "reasoning": "Passage 0 states that snapshots are retained for seven days.",
  "citations": [
    {
      "index": 0,
      "quote": "Snapshots are retained for seven days."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "ArchiveBox creates hourly snapshots.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "ArchiveBox retains snapshots for seven days.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-02

**Sources**

Passage 0

```text
RelayGate retries GET requests after a connection reset. It never retries POST requests.
```

**Generated answer**

```text
RelayGate retries GET requests after a connection reset, but never retries POST requests.
```

**Approved gold**

```json
[
  {
    "claim_text": "RelayGate retries GET requests after a connection reset.",
    "verdict": "SUPPORTED",
    "reasoning": "The source explicitly retries GET requests after a connection reset, matching the answer's request type and condition.",
    "citations": [
      {
        "index": 0,
        "quote": "RelayGate retries GET requests after a connection reset. It never retries POST requests."
      }
    ],
    "id": "g1",
    "annotation_reason": "The connection-reset condition is part of the fact; this does not establish retries after every kind of failure."
  },
  {
    "claim_text": "RelayGate never retries POST requests.",
    "verdict": "SUPPORTED",
    "reasoning": "The source states that RelayGate never retries POST requests.",
    "citations": [
      {
        "index": 0,
        "quote": "RelayGate retries GET requests after a connection reset. It never retries POST requests."
      }
    ],
    "id": "g2",
    "annotation_reason": "Resolve It to RelayGate and preserve never; the exception for POST is independent of the supported GET behavior."
  }
]
```

### dev-02 / A

Review ID: `177a38333d9cd6ab`

Output hash: `f33a0644d46cbea8e7cb0bf5828a6ca286bc00e857aa22ae63a30effc65f6588`

**Prediction 0**

```json
{
  "claim_text": "RelayGate retries GET requests after a connection reset, but never retries POST requests.",
  "verdict": "SUPPORTED",
  "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
  "citations": [
    {
      "index": 0,
      "quote": "RelayGate retries GET requests after a connection reset."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "RelayGate retries GET requests after a connection reset, but never retries POST requests.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-02 / B

Review ID: `6132bd1623180349`

Output hash: `e5e1e0f3681f5b6ef441d67b410a4791fef27fd800b8f361ddd0aa734e5c2dbb`

**Prediction 0**

```json
{
  "claim_text": "RelayGate retries GET requests after a connection reset.",
  "verdict": "SUPPORTED",
  "reasoning": "Passage 0 states that RelayGate retries GET requests after a connection reset.",
  "citations": [
    {
      "index": 0,
      "quote": "RelayGate retries GET requests after a connection reset."
    }
  ]
}
```

**Prediction 1**

```json
{
  "claim_text": "RelayGate never retries POST requests.",
  "verdict": "SUPPORTED",
  "reasoning": "Passage 0 states that RelayGate never retries POST requests.",
  "citations": [
    {
      "index": 0,
      "quote": "It never retries POST requests."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "RelayGate retries GET requests after a connection reset.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "RelayGate never retries POST requests.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-03

**Sources**

Passage 0

```text
TaskDock permits at most four active workers. Additional workers remain queued.
```

**Generated answer**

```text
TaskDock permits five active workers. Additional workers remain queued.
```

**Approved gold**

```json
[
  {
    "claim_text": "TaskDock permits five active workers.",
    "verdict": "CONTRADICTED",
    "reasoning": "The specification permits at most four active TaskDock workers, so permitting five active workers exceeds the stated maximum.",
    "citations": [
      {
        "index": 0,
        "quote": "TaskDock permits at most four active workers. Additional workers remain queued."
      }
    ],
    "id": "g1",
    "annotation_reason": "Four is an inclusive upper bound on active workers, not a lower bound or a limit on queued workers."
  },
  {
    "claim_text": "Additional TaskDock workers remain queued.",
    "verdict": "SUPPORTED",
    "reasoning": "The specification explicitly states that additional workers remain queued.",
    "citations": [
      {
        "index": 0,
        "quote": "TaskDock permits at most four active workers. Additional workers remain queued."
      }
    ],
    "id": "g2",
    "annotation_reason": "Additional workers refers to workers beyond TaskDock's active-worker limit; this remains supported despite the answer's incorrect number."
  }
]
```

### dev-03 / A

Review ID: `7937014053aa8714`

Output hash: `1d8534e71662179852272be10dffef9c5396a6f084ac7d429bf800cd5446901d`

**Prediction 0**

```json
{
  "claim_text": "TaskDock permits five active workers.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Prediction 1**

```json
{
  "claim_text": "Additional workers remain queued.",
  "verdict": "SUPPORTED",
  "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
  "citations": [
    {
      "index": 0,
      "quote": "Additional workers remain queued."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "TaskDock permits five active workers.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "Additional workers remain queued.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-03 / B

Review ID: `9939ea298b701d8e`

Output hash: `d0122f0e1a7d3fb65a0439bdd166e792564843dda5a8fc6543eb262e8c6b6888`

**Prediction 0**

```json
{
  "claim_text": "TaskDock permits five active workers.",
  "verdict": "CONTRADICTED",
  "reasoning": "The context states TaskDock permits at most four active workers, not five.",
  "citations": [
    {
      "index": 0,
      "quote": "TaskDock permits at most four active workers."
    }
  ]
}
```

**Prediction 1**

```json
{
  "claim_text": "Additional workers remain queued.",
  "verdict": "SUPPORTED",
  "reasoning": "The context states that additional workers remain queued.",
  "citations": [
    {
      "index": 0,
      "quote": "Additional workers remain queued."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "TaskDock permits five active workers.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "Additional workers remain queued.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-04

**Sources**

Passage 0

```text
CedarCache does not persist entries across restarts.
```

**Generated answer**

```text
CedarCache persists entries across restarts.
```

**Approved gold**

```json
[
  {
    "claim_text": "CedarCache persists entries across restarts.",
    "verdict": "CONTRADICTED",
    "reasoning": "The source says CedarCache does not persist entries across restarts, directly opposing the answer's persistence claim.",
    "citations": [
      {
        "index": 0,
        "quote": "CedarCache does not persist entries across restarts."
      }
    ],
    "id": "g1",
    "annotation_reason": "Compare the same cache, entries, and restart condition; the answer reverses an explicit negation."
  }
]
```

### dev-04 / A

Review ID: `b91c622410a45190`

Output hash: `04fb314023354f58bf14f818f84f88d2895121fa5fe2b77f99023c162b89e130`

**Prediction 0**

```json
{
  "claim_text": "CedarCache persists entries across restarts.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "CedarCache persists entries across restarts.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-04 / B

Review ID: `516531cf82eceece`

Output hash: `9875f5db31865a5c25d4bc305a065b7797e8b64641106d6aac36c592f036ccb0`

**Prediction 0**

```json
{
  "claim_text": "CedarCache persists entries across restarts.",
  "verdict": "CONTRADICTED",
  "reasoning": "Passage 0 states that CedarCache does not persist entries across restarts, which directly contradicts the claim.",
  "citations": [
    {
      "index": 0,
      "quote": "CedarCache does not persist entries across restarts."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "CedarCache persists entries across restarts.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-05

**Sources**

Passage 0

```text
CachePebble writes entries to a local file after each update.
```

**Generated answer**

```text
CachePebble writes entries to a local file after each update. Its files are encrypted with AES-256.
```

**Approved gold**

```json
[
  {
    "claim_text": "CachePebble writes entries to a local file after each update.",
    "verdict": "SUPPORTED",
    "reasoning": "The source explicitly writes CachePebble entries to a local file after each update.",
    "citations": [
      {
        "index": 0,
        "quote": "CachePebble writes entries to a local file after each update."
      }
    ],
    "id": "g1",
    "annotation_reason": "Preserve the after-each-update condition; the separate encryption assertion has a different evidential status."
  },
  {
    "claim_text": "CachePebble files are encrypted with AES-256.",
    "verdict": "UNSUPPORTED",
    "reasoning": "The source describes local file writes but gives no encryption algorithm or encryption guarantee.",
    "citations": [],
    "id": "g2",
    "annotation_reason": "Local storage neither establishes nor rules out AES-256; absence of evidence is not a contradiction."
  }
]
```

### dev-05 / A

Review ID: `68f651aaae7a5955`

Output hash: `f450e1cfb84d6661812da01cdbe9724c6a3fd12aaa9ea9f1e3d49e929baf8d80`

**Prediction 0**

```json
{
  "claim_text": "CachePebble writes entries to a local file after each update.",
  "verdict": "SUPPORTED",
  "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
  "citations": [
    {
      "index": 0,
      "quote": "CachePebble writes entries to a local file after each update."
    }
  ]
}
```

**Prediction 1**

```json
{
  "claim_text": "Its files are encrypted with AES-256.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "CachePebble writes entries to a local file after each update.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "Its files are encrypted with AES-256.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-05 / B

Review ID: `94dcc5004e7081f7`

Output hash: `17872aa4278fb8cb930d5de6ac93a5a44d2b0a881703c7b2fd590e475fcd4f4e`

**Prediction 0**

```json
{
  "claim_text": "CachePebble writes entries to a local file after each update.",
  "verdict": "SUPPORTED",
  "reasoning": "The first passage states directly that CachePebble writes entries to a local file after each update.",
  "citations": [
    {
      "index": 0,
      "quote": "CachePebble writes entries to a local file after each update."
    }
  ]
}
```

**Prediction 1**

```json
{
  "claim_text": "CachePebble's files are encrypted with AES-256.",
  "verdict": "UNSUPPORTED",
  "reasoning": "The context passage does not mention encryption or AES-256.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "CachePebble writes entries to a local file after each update.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  },
  {
    "prediction_index": 1,
    "text": "CachePebble's files are encrypted with AES-256.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-06

**Sources**

Passage 0

```text
WireFin reuses an established connection for subsequent requests.
```

**Generated answer**

```text
WireFin uses Brotli compression for request payloads.
```

**Approved gold**

```json
[
  {
    "claim_text": "WireFin uses Brotli compression for request payloads.",
    "verdict": "UNSUPPORTED",
    "reasoning": "The only supplied behavior is connection reuse; the source does not specify request compression or Brotli.",
    "citations": [],
    "id": "g1",
    "annotation_reason": "Connection reuse and payload compression are independent properties, so neither support nor direct refutation is available."
  }
]
```

### dev-06 / A

Review ID: `8be92893f678f858`

Output hash: `43b012ce8475d6432465a94866f7a387a036fa9f98a98694981a86e836c5241f`

**Prediction 0**

```json
{
  "claim_text": "WireFin uses Brotli compression for request payloads.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "WireFin uses Brotli compression for request payloads.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-06 / B

Review ID: `27b90bc3895b86fe`

Output hash: `607b3582f730436050a39a5334b8332557252a316d7cdb9dfbe07ce6d988e6e3`

**Prediction 0**

```json
{
  "claim_text": "WireFin uses Brotli compression for request payloads.",
  "verdict": "UNSUPPORTED",
  "reasoning": "The context passages only state that WireFin reuses an established connection for subsequent requests; nothing about Brotli compression or request payload compression is mentioned.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "WireFin uses Brotli compression for request payloads.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-07

**Sources**

Passage 0

```text
Service Juniper runs in mode Q.
```

Passage 1

```text
Every service in mode Q encrypts its stored payloads.
```

**Generated answer**

```text
Service Juniper encrypts its stored payloads.
```

**Approved gold**

```json
[
  {
    "claim_text": "Service Juniper encrypts its stored payloads.",
    "verdict": "SUPPORTED",
    "reasoning": "Passage 0 places Juniper in mode Q; passage 1 says every service in Q encrypts stored payloads. Together they entail the claim.",
    "citations": [
      {
        "index": 0,
        "quote": "Service Juniper runs in mode Q."
      },
      {
        "index": 1,
        "quote": "Every service in mode Q encrypts its stored payloads."
      }
    ],
    "id": "g1",
    "annotation_reason": "Both the service's membership and the universal encryption rule are necessary; citing either passage alone omits a premise."
  }
]
```

### dev-07 / A

Review ID: `6a378da1c1b4a246`

Output hash: `d611784c2bd4c653e506bf283b0d93c11fc6f540aca2bcbfe9d5079a1e2dcc8d`

**Prediction 0**

```json
{
  "claim_text": "Service Juniper encrypts its stored payloads.",
  "verdict": "SUPPORTED",
  "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
  "citations": [
    {
      "index": 1,
      "quote": "Every service in mode Q encrypts its stored payloads."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "Service Juniper encrypts its stored payloads.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-07 / B

Review ID: `cb7119818664075d`

Output hash: `f784f0dde6ac011e6ab3ba7fd8bf0e68dafeb1d2cab3a240fa83d99a50dfb9d8`

**Prediction 0**

```json
{
  "claim_text": "Service Juniper encrypts its stored payloads.",
  "verdict": "SUPPORTED",
  "reasoning": "Passage 0 places Service Juniper in mode Q, and passage 1 states every service in mode Q encrypts its stored payloads, so the claim follows.",
  "citations": [
    {
      "index": 0,
      "quote": "Service Juniper runs in mode Q."
    },
    {
      "index": 1,
      "quote": "Every service in mode Q encrypts its stored payloads."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "Service Juniper encrypts its stored payloads.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

## dev-08

**Sources**

Passage 0

```text
The recovery worker runs on host Maple.
```

Passage 1

```text
Host Maple is located in region West.
```

**Generated answer**

```text
The recovery worker runs in region West.
```

**Approved gold**

```json
[
  {
    "claim_text": "The recovery worker runs in region West.",
    "verdict": "SUPPORTED",
    "reasoning": "The worker runs on Maple according to passage 0, and Maple is in West according to passage 1, placing the worker in West.",
    "citations": [
      {
        "index": 0,
        "quote": "The recovery worker runs on host Maple."
      },
      {
        "index": 1,
        "quote": "Host Maple is located in region West."
      }
    ],
    "id": "g1",
    "annotation_reason": "The conclusion follows by joining the same host Maple across the two passages; both location premises are required."
  }
]
```

### dev-08 / A

Review ID: `bef10536635f486e`

Output hash: `7658d41b97de788a8231bc7a7e999c3a97800de91abdad98a0f8df66694bb776`

**Prediction 0**

```json
{
  "claim_text": "The recovery worker runs in region West.",
  "verdict": "UNSUPPORTED",
  "reasoning": "No sufficiently similar source sentence was found by the lexical heuristic.",
  "citations": []
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "The recovery worker runs in region West.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```

### dev-08 / B

Review ID: `928ca1f6a9473b8d`

Output hash: `c0fe6144ed5bc09e4dff4ea7066e985b18fb9d04465eed4c75e373c0d57f0845`

**Prediction 0**

```json
{
  "claim_text": "The recovery worker runs in region West.",
  "verdict": "SUPPORTED",
  "reasoning": "Passage 0 states the recovery worker runs on host Maple, and passage 1 states Host Maple is located in region West, so the claim follows by linking the two passages.",
  "citations": [
    {
      "index": 0,
      "quote": "The recovery worker runs on host Maple."
    },
    {
      "index": 1,
      "quote": "Host Maple is located in region West."
    }
  ]
}
```

**Pending alignment and evidence review**

```json
[
  {
    "prediction_index": 0,
    "text": "The recovery worker runs in region West.",
    "gold_id": null,
    "evidence_sufficient": null,
    "note": ""
  }
]
```
