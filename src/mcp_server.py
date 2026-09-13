"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
Chủ đề: Trợ lý Nhân sự VinFast (HR Assistant).
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPHRServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    """
    def __init__(self, server_name: str = "vinfast-hr-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] Thực thi request gọi Tool theo chuẩn MCP JSON-RPC 2.0
        """
        raw_result = dispatch_tool_call(tool_name, arguments)
        try:
            content = json.loads(raw_result)
        except json.JSONDecodeError:
            content = {"status": "EXECUTION_ERROR", "error": "Tool trả về dữ liệu không phải JSON hợp lệ."}
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


# Giữ alias tên cũ để tương thích với tài liệu CODELAB
MCPAcademicServer = MCPHRServer


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (vinfast-hr-mcp-server)")
    print("==========================================================")
    
    server = MCPHRServer()
    tools = server.list_tools()
    print(f"✅ Khởi tạo thành công MCP Server: {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố: {len(tools)}")
    for t in tools:
        print(f"   - {t['name']}: {t['description']}")

    # Kiểm tra schema của tool tạo đơn nghỉ phép
    leave_tool = next((t for t in tools if t.get("name") == "create_leave_request"), None)
    if leave_tool and not leave_tool.get("parameters", {}).get("properties"):
        print("⏳ [TODO 1.2]: Tool 'create_leave_request' chưa được định nghĩa properties trong 'src/tools.py'.")
    else:
        print("✅ [TODO 1.2]: Tool 'create_leave_request' đã có schema đầy đủ.")

    # Kiểm tra call_tool
    test_result = server.call_tool("leave_balance_query", {"employee_id": "VF2026001"})
    if not test_result:
        print("⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng.")
    else:
        print(f"✅ [TODO 2.1]: Test dispatch tool 'leave_balance_query' thành công:")
        print(f"   Phản hồi JSON-RPC: {json.dumps(test_result, ensure_ascii=False)}")
