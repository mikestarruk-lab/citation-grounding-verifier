"""Offline scoring uses independent raw citation checks, not the service validator."""

from collections import Counter

from .dataset import digest


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def raw_citations(output, passages):
    valid = total = 0
    if not isinstance(output, dict) or not isinstance(output.get("claims"), list):
        return valid, total
    for claim in output["claims"]:
        if not isinstance(claim, dict) or not isinstance(claim.get("citations"), list):
            continue
        for citation in claim["citations"]:
            total += 1
            if not isinstance(citation, dict):
                continue
            index, quote = citation.get("index"), citation.get("quote")
            if (
                type(index) is int
                and 0 <= index < len(passages)
                and isinstance(quote, str)
                and quote.strip()
                and quote in passages[index]
            ):
                valid += 1
    return valid, total


def output_hash(record):
    return digest(
        {"status": record["status"], "output": record.get("output"), "error": record.get("error")}
    )


def review_template(run, cases_by_id):
    packets = []
    for record in run["records"]:
        if record["status"] != "ok":
            continue
        case = cases_by_id[record["case_id"]]
        h = output_hash(record)
        claims = record["output"]["claims"]
        packets.append(
            {
                "review_id": digest([run["dataset_hash"], case.id, h])[:16],
                "case_id": case.id,
                "dataset_hash": run["dataset_hash"],
                "output_hash": h,
                "status": "pending",
                "reviewer": None,
                "context_passages": case.context_passages,
                "generated_answer": case.generated_answer,
                "gold_claims": [g.model_dump(mode="json") for g in case.gold_claims],
                "prediction": record["output"],
                "units": [
                    {
                        "prediction_index": i,
                        "text": c["claim_text"],
                        "gold_id": None,
                        "evidence_sufficient": None,
                        "note": "",
                    }
                    for i, c in enumerate(claims)
                ],
            }
        )
    return sorted(packets, key=lambda p: p["review_id"])


def score(run: dict, cases: list, reviews: list[dict] | None = None):
    if run["dataset_hash"] != digest([c.model_dump(mode="json") for c in cases]):
        raise ValueError("dataset hash mismatch")
    by_case = {c.id: c for c in cases}
    records = run["records"]
    if len(records) != len(cases) or {r["case_id"] for r in records} != set(by_case):
        raise ValueError("run must contain exactly one record for every case, including failures")
    review_map = {}
    for r in reviews or []:
        key = (r["case_id"], r["output_hash"])
        if key in review_map:
            raise ValueError("duplicate review")
        review_map[key] = r
    active_keys = {(r["case_id"], output_hash(r)) for r in records if r["status"] == "ok"}
    if set(review_map) - active_keys:
        raise ValueError("stale or unrelated review: output hash mismatch")

    counts = Counter()
    counts["cases"] = len(cases)
    counts["gold_facts"] = sum(len(c.gold_claims) for c in cases)
    labels = Counter(g.verdict.value for c in cases for g in c.gold_claims)
    latencies, first_latencies, warm_latencies = [], [], []
    confirmed_cost = 0.0
    outstanding_reservations = 0.0
    pending = []
    confusion = {label: Counter() for label in ("SUPPORTED", "CONTRADICTED", "UNSUPPORTED")}
    for record in records:
        case = by_case[record["case_id"]]
        trace = record.get("trace", {})
        if "latency_seconds" in trace:
            latencies.append(trace["latency_seconds"])
        attempts = trace.get("attempts", [])
        counts["calls"] += len(attempts)
        counts["repaired_requests"] += bool(trace.get("repair_count"))
        for attempt in attempts:
            cost = attempt.get("cost_usd")
            if cost is None:
                outstanding_reservations += attempt.get("reserved_usd", 0)
                counts["unpriced_calls"] += 1
            else:
                confirmed_cost += cost
            if "latency_seconds" in attempt:
                (
                    first_latencies if attempt.get("first_request_in_client") else warm_latencies
                ).append(attempt["latency_seconds"])
            usage = attempt.get("usage", {})
            for field in (
                "input_tokens",
                "output_tokens",
                "cache_read_input_tokens",
                "cache_creation_input_tokens",
            ):
                counts[field] += usage.get(field) or 0
        first = trace.get("first_output")
        for prefix, output in (("first", first), ("final", record.get("output"))):
            valid, total = raw_citations(output, case.context_passages)
            counts[f"{prefix}_valid_quotes"] += valid
            counts[f"{prefix}_quotes"] += total

        if record["status"] != "ok":
            counts["fn"] += len(case.gold_claims)
            for g in case.gold_claims:
                confusion[g.verdict.value]["ERROR"] += 1
            continue
        counts["successes"] += 1
        predictions = record["output"]["claims"]
        if run["mode"] == "gold":
            if [p["claim_text"] for p in predictions] != [g.claim_text for g in case.gold_claims]:
                raise ValueError("fixed gold claims were changed")
            for gold, prediction in zip(case.gold_claims, predictions, strict=True):
                confusion[gold.verdict.value][prediction["verdict"]] += 1
            continue
        review = review_map.get((case.id, output_hash(record)))
        if not review or review.get("status") != "approved" or not review.get("reviewer"):
            pending.append(case.id)
            continue
        if review["dataset_hash"] != run["dataset_hash"]:
            raise ValueError("stale review dataset hash")
        if review.get("prediction") != record["output"]:
            raise ValueError("review prediction was edited")
        if review.get("gold_claims") != [g.model_dump(mode="json") for g in case.gold_claims]:
            raise ValueError("review gold claims were edited")
        units = review["units"]
        indices = [u["prediction_index"] for u in units]
        if (
            any(type(i) is not int or not 0 <= i < len(predictions) for i in indices)
            or set(indices) != set(range(len(predictions)))
            or indices != sorted(indices)
        ):
            raise ValueError("review units must cover every prediction in original order")
        multiplicity = Counter(indices)
        counts["atomic_predictions"] += sum(n == 1 for n in multiplicity.values())
        counts["predictions"] += len(predictions)
        counts["predicted_units"] += len(units)
        gold_by_id = {g.id: g for g in case.gold_claims}
        seen, correct = set(), set()
        for unit in units:
            if not isinstance(unit.get("text"), str) or not unit["text"].strip():
                raise ValueError("every reviewed unit needs its faithfully preserved text")
            prediction = predictions[unit["prediction_index"]]
            if prediction["verdict"] != "UNSUPPORTED":
                if type(unit.get("evidence_sufficient")) is not bool:
                    raise ValueError("support/contradiction units need evidence sufficiency review")
                counts["evidence_units"] += 1
                counts["sufficient_evidence"] += unit["evidence_sufficient"]
            gid = unit.get("gold_id")
            if gid is not None and gid not in gold_by_id:
                raise ValueError("unknown gold ID")
            if gid is None or gid in seen:
                counts["fp"] += 1
                continue
            seen.add(gid)
            gold = gold_by_id[gid]
            verdict = prediction["verdict"]
            confusion[gold.verdict.value][verdict] += 1
            counts["covered"] += 1
            if verdict == gold.verdict.value:
                counts["tp"] += 1
                correct.add(gid)
            else:
                counts["fp"] += 1
            counts["false_support"] += gold.verdict.value != "SUPPORTED" and verdict == "SUPPORTED"
            counts["false_rejection"] += (
                gold.verdict.value == "SUPPORTED" and verdict == "UNSUPPORTED"
            )
        counts["fn"] += len(gold_by_id) - len(correct)
        for gid in set(gold_by_id) - seen:
            confusion[gold_by_id[gid].verdict.value]["MISSING"] += 1

    def quantile(values, q):
        if not values:
            return None
        values = sorted(values)
        point = (len(values) - 1) * q
        lo = int(point)
        return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (point - lo)

    result = {
        "mode": run["mode"],
        "method": run["method"],
        "cases": len(cases),
        "success_rate": ratio(counts["successes"], counts["cases"]),
        "repair_rate": ratio(counts["repaired_requests"], counts["cases"]),
        "confirmed_cost_usd": confirmed_cost,
        "unsettled_reserved_usd": outstanding_reservations,
        "first_quote_validity": ratio(counts["first_valid_quotes"], counts["first_quotes"]),
        "final_quote_validity": ratio(counts["final_valid_quotes"], counts["final_quotes"]),
        "latency_sample_size": len(latencies),
        "p50_seconds": quantile(latencies, 0.50),
        "p95_seconds": quantile(latencies, 0.95),
        "first_client_call_seconds": first_latencies,
        "warm_call_p50_seconds": quantile(warm_latencies, 0.50),
        "pending_reviews": pending,
        "counts": dict(counts),
    }
    if run["mode"] == "gold":
        per_label = {}
        for label in confusion:
            tp = confusion[label][label]
            fn = sum(confusion[label].values()) - tp
            fp = sum(row[label] for actual, row in confusion.items() if actual != label)
            per_label[label] = ratio(2 * tp, 2 * tp + fp + fn)
        scores = [x for x in per_label.values() if x is not None]
        result.update(
            semantic_status="automatic_fixed_claim_diagnostic",
            per_label_f1=per_label,
            macro_f1=sum(scores) / len(scores) if scores else None,
            confusion={k: dict(v) for k, v in confusion.items()},
        )
    elif pending:
        result["semantic_status"] = "pending_human_review"
    else:
        result.update(
            semantic_status="reviewed",
            precision=ratio(counts["tp"], counts["tp"] + counts["fp"]),
            recall=ratio(counts["tp"], counts["gold_facts"]),
            f1=ratio(2 * counts["tp"], 2 * counts["tp"] + counts["fp"] + counts["fn"]),
            coverage=ratio(counts["covered"], counts["gold_facts"]),
            false_support_rate=ratio(
                counts["false_support"], labels["CONTRADICTED"] + labels["UNSUPPORTED"]
            ),
            false_rejection_rate=ratio(counts["false_rejection"], labels["SUPPORTED"]),
            evidence_sufficiency=ratio(counts["sufficient_evidence"], counts["evidence_units"]),
            atomicity=ratio(counts["atomic_predictions"], counts["predictions"]),
            confusion={k: dict(v) for k, v in confusion.items()},
        )
    return result
