# Test Suite

<system_context>
Comprehensive test suite for Phase 1 foundation components including unit tests, integration tests, performance validation, and MCP server testing.
</system_context>

<critical_notes>
- All tests must run independently without dependencies
- Performance tests validate against specific targets from Advanced-Implementation-Guide.md
- Use pytest framework for all test execution
- Mock external dependencies like Ursina for unit tests
</critical_notes>

<file_map>
Unit tests: @tests/unit/
Integration tests: @tests/integration/
Performance tests: @tests/performance/
MCP tests: @tests/mcp/
Test utilities: @tests/utils/
</file_map>

<paved_path>
1. Run unit tests first to validate individual components
2. Execute integration tests for system interactions
3. Perform performance validation against targets
4. Test MCP server functionality
5. Generate comprehensive test report
</paved_path>

<patterns>
```python
# Standard test pattern
def test_component_functionality():
    # Arrange
    component = create_test_component()
    
    # Act
    result = component.perform_action()
    
    # Assert
    assert result.is_valid()
    assert_performance_target_met()
```
</patterns>

<workflow>
Test execution order: unit → integration → performance → mcp → report
</workflow>