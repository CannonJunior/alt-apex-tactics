# Performance Tests

<system_context>
Performance validation tests for Phase 1 systems against specific targets from Advanced-Implementation-Guide.md.
</system_context>

<critical_notes>
- Validates <1ms stat calculations
- Validates <2ms pathfinding on 10x10 grids
- Tests 60 FPS maintenance with 50+ entities
- Measures memory usage and cleanup
</critical_notes>

<file_map>
Performance suite: @tests/performance/performance_suite.py
Benchmarks: @tests/performance/benchmarks.py
</file_map>

<patterns>
```python
# Performance test pattern
def test_performance_target():
    start_time = time.perf_counter()
    # ... perform operation
    elapsed = time.perf_counter() - start_time
    assert elapsed < TARGET_TIME
```
</patterns>