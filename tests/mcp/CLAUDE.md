# MCP Server Tests

<system_context>
Tests for Model Context Protocol (MCP) server integration with tactical RPG AI systems.
</system_context>

<critical_notes>
- Tests must handle FastMCP import gracefully with fallback behavior
- Mock MCP server responses for consistent testing
- Validate all tactical analysis tools and resources
</critical_notes>

<file_map>
Test files: @tests/mcp/test_tactical_server.py
Mock utilities: @tests/mcp/mock_mcp.py
</file_map>

<patterns>
```python
# MCP server test pattern
@pytest.fixture
def mock_mcp_server():
    with patch('src.ai.mcp.tactical_server.FastMCP'):
        yield MockMCPServer()
```
</patterns>