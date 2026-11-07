import time
import statistics
import pytest

pytestmark = pytest.mark.slow

CYCLES = 100


def _mock_detect():
    time.sleep(0.001)
    return True


def test_mock_detection_100_cycles():
    latencies = []
    for _ in range(CYCLES):
        t0 = time.perf_counter()
        _mock_detect()
        latencies.append(time.perf_counter() - t0)

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(CYCLES * 0.95) - 1]
    p99 = latencies[int(CYCLES * 0.99) - 1]

    assert p50 < 0.1
    assert p95 < 0.2
    assert p99 < 0.5


def test_no_memory_growth_100_cycles():
    psutil = pytest.importorskip("psutil")
    import os

    proc = psutil.Process(os.getpid())
    rss_before = proc.memory_info().rss / (1024 * 1024)

    for _ in range(CYCLES):
        _mock_detect()

    rss_after = proc.memory_info().rss / (1024 * 1024)
    growth_mb = rss_after - rss_before
    assert growth_mb < 50, f"RSS grew {growth_mb:.1f}MB over {CYCLES} cycles"
