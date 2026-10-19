# Candidate output delta review

Unchanged exact output hashes retain their existing approvals. Changed packets
remain pending. Alignment is projected only because text/order is unchanged.
Review the full context, verdict, reasoning and citations below before approval.

## dev-04

```json
{
  "review_id": "05ec364d3666c813",
  "case_id": "dev-04",
  "dataset_hash": "e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c",
  "output_hash": "3a481cbeaf30d49819708559345f56e69271c59abe22b2a762e529ffcef4bc53",
  "status": "pending",
  "reviewer": null,
  "context_passages": [
    "CedarCache does not persist entries across restarts."
  ],
  "generated_answer": "CedarCache persists entries across restarts.",
  "gold_claims": [
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
  ],
  "prediction": {
    "claims": [
      {
        "claim_text": "CedarCache persists entries across restarts.",
        "verdict": "SUPPORTED",
        "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
        "citations": [
          {
            "index": 0,
            "quote": "CedarCache does not persist entries across restarts."
          }
        ]
      }
    ]
  },
  "units": [
    {
      "prediction_index": 0,
      "text": "CedarCache persists entries across restarts.",
      "gold_id": "g1",
      "evidence_sufficient": null,
      "note": "New output needs owner evidence review."
    }
  ],
  "alignment_source": {
    "review_id": "b91c622410a45190",
    "output_hash": "04fb314023354f58bf14f818f84f88d2895121fa5fe2b77f99023c162b89e130",
    "note": "Semantic alignment copied for unchanged text; new output remains pending."
  }
}
```

## dev-08

```json
{
  "review_id": "4463e1ea6ed4ba34",
  "case_id": "dev-08",
  "dataset_hash": "e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c",
  "output_hash": "af4719a7c3ee5d9bda3c1e7d08b87498e2afe01280bddd5f9c88bb141e987453",
  "status": "pending",
  "reviewer": null,
  "context_passages": [
    "The recovery worker runs on host Maple.",
    "Host Maple is located in region West."
  ],
  "generated_answer": "The recovery worker runs in region West.",
  "gold_claims": [
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
  ],
  "prediction": {
    "claims": [
      {
        "claim_text": "The recovery worker runs in region West.",
        "verdict": "SUPPORTED",
        "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
        "citations": [
          {
            "index": 0,
            "quote": "The recovery worker runs on host Maple."
          }
        ]
      }
    ]
  },
  "units": [
    {
      "prediction_index": 0,
      "text": "The recovery worker runs in region West.",
      "gold_id": "g1",
      "evidence_sufficient": null,
      "note": "New output needs owner evidence review."
    }
  ],
  "alignment_source": {
    "review_id": "bef10536635f486e",
    "output_hash": "7658d41b97de788a8231bc7a7e999c3a97800de91abdad98a0f8df66694bb776",
    "note": "Semantic alignment copied for unchanged text; new output remains pending."
  }
}
```

## dev-03

```json
{
  "review_id": "7392a545f2d0f4c7",
  "case_id": "dev-03",
  "dataset_hash": "e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c",
  "output_hash": "2069146ca5d7939801d3acf1976cc198a9569a21b9debbea3956ee67ededa5da",
  "status": "pending",
  "reviewer": null,
  "context_passages": [
    "TaskDock permits at most four active workers. Additional workers remain queued."
  ],
  "generated_answer": "TaskDock permits five active workers. Additional workers remain queued.",
  "gold_claims": [
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
  ],
  "prediction": {
    "claims": [
      {
        "claim_text": "TaskDock permits five active workers.",
        "verdict": "SUPPORTED",
        "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
        "citations": [
          {
            "index": 0,
            "quote": "TaskDock permits at most four active workers."
          }
        ]
      },
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
    ]
  },
  "units": [
    {
      "prediction_index": 0,
      "text": "TaskDock permits five active workers.",
      "gold_id": "g1",
      "evidence_sufficient": null,
      "note": "New output needs owner evidence review."
    },
    {
      "prediction_index": 1,
      "text": "Additional workers remain queued.",
      "gold_id": "g2",
      "evidence_sufficient": null,
      "note": "New output needs owner evidence review."
    }
  ],
  "alignment_source": {
    "review_id": "7937014053aa8714",
    "output_hash": "1d8534e71662179852272be10dffef9c5396a6f084ac7d429bf800cd5446901d",
    "note": "Semantic alignment copied for unchanged text; new output remains pending."
  }
}
```

## dev-01

```json
{
  "review_id": "c79c302ce6db3b77",
  "case_id": "dev-01",
  "dataset_hash": "e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c",
  "output_hash": "73cf15b266d7a4fb4f342adb6e77c773d0b571040d603ea25c00ebe8c5f1d62e",
  "status": "pending",
  "reviewer": null,
  "context_passages": [
    "ArchiveBox creates a snapshot every hour. Snapshots are retained for seven days."
  ],
  "generated_answer": "ArchiveBox creates hourly snapshots. It retains snapshots for seven days.",
  "gold_claims": [
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
  ],
  "prediction": {
    "claims": [
      {
        "claim_text": "ArchiveBox creates hourly snapshots.",
        "verdict": "SUPPORTED",
        "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
        "citations": [
          {
            "index": 0,
            "quote": "ArchiveBox creates a snapshot every hour."
          }
        ]
      },
      {
        "claim_text": "It retains snapshots for seven days.",
        "verdict": "SUPPORTED",
        "reasoning": "Lexical similarity exceeds the configured threshold; this heuristic does not establish semantic entailment.",
        "citations": [
          {
            "index": 0,
            "quote": "Snapshots are retained for seven days."
          }
        ]
      }
    ]
  },
  "units": [
    {
      "prediction_index": 0,
      "text": "ArchiveBox creates hourly snapshots.",
      "gold_id": "g1",
      "evidence_sufficient": null,
      "note": "New output needs owner evidence review."
    },
    {
      "prediction_index": 1,
      "text": "It retains snapshots for seven days.",
      "gold_id": "g2",
      "evidence_sufficient": null,
      "note": "New output needs owner evidence review."
    }
  ],
  "alignment_source": {
    "review_id": "54375d9ba5082f3a",
    "output_hash": "b1416fb783e67787b8c42c0d14e2e003e5a2c63a9094afcfa2f24639c35a0fb7",
    "note": "Semantic alignment copied for unchanged text; new output remains pending."
  }
}
```
