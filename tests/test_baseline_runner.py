from experiments.run_baseline import baseline_record


def test_baseline_record_has_comparable_schema():
    row = baseline_record(prompt="Mostre pagamentos", sql="SELECT * FROM payment", allowed=False, latency_ms=12.5)
    assert set(["mode", "prompt", "sql", "allowed", "latency_ms"]).issubset(row)
    assert row["mode"] == "baseline_direct_sql"
