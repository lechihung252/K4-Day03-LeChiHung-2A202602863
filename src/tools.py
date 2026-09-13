"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
Chủ đề: Trợ lý Nhân sự VinFast (HR Assistant) — tra cứu ngày phép, chính sách bảo hiểm, tạo đơn nghỉ phép.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu số ngày phép còn lại của nhân viên
    {
        "name": "leave_balance_query",
        "description": "Tra cứu hồ sơ nhân sự và số ngày phép năm còn lại của nhân viên VinFast bằng mã nhân viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên cần tra cứu (ví dụ: 'VF2026001')"
                }
            },
            "required": ["employee_id"]
        }
    },

    # Tool 2: Tra cứu chính sách bảo hiểm của nhân viên
    {
        "name": "insurance_policy_query",
        "description": "Tra cứu gói bảo hiểm (BHXH, BHYT và bảo hiểm sức khỏe VinFast Care) mà nhân viên đang được hưởng.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên cần tra cứu chính sách bảo hiểm (ví dụ: 'VF2026001')"
                }
            },
            "required": ["employee_id"]
        }
    },

    # Tool 3: Tạo đơn xin nghỉ phép (hành động ghi vào hệ thống HR)
    {
        "name": "create_leave_request",
        "description": "Tạo đơn xin nghỉ phép cho nhân viên VinFast. Chỉ gọi khi đã xác định đủ mã nhân viên, ngày bắt đầu và ngày kết thúc.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên xin nghỉ (ví dụ: 'VF2026001')"
                },
                "start_date": {
                    "type": "string",
                    "description": "Ngày bắt đầu nghỉ, định dạng DD/MM/YYYY (ví dụ: '15/09/2026')"
                },
                "end_date": {
                    "type": "string",
                    "description": "Ngày kết thúc nghỉ, định dạng DD/MM/YYYY (ví dụ: '17/09/2026')"
                },
                "leave_type": {
                    "type": "string",
                    "enum": ["annual", "sick", "unpaid"],
                    "description": "Loại nghỉ phép: 'annual' (phép năm), 'sick' (nghỉ ốm), 'unpaid' (nghỉ không lương)"
                },
                "reason": {
                    "type": "string",
                    "description": "Lý do xin nghỉ phép"
                }
            },
            "required": ["employee_id", "start_date", "end_date", "leave_type"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "VF2026001": {
        "full_name": "Nguyễn Văn An",
        "department": "Phòng Kỹ thuật Pin (Battery Engineering)",
        "position": "Kỹ sư Phần mềm",
        "email": "an.nv@vinfast.vn",
        "manager": "Trần Minh Quân",
        "annual_leave_total": 15,
        "annual_leave_used": 6,
        "insurance": {
            "social_insurance": "Đang tham gia BHXH bắt buộc (đóng từ 01/2024)",
            "health_insurance": "BHYT — Bệnh viện Vinmec Times City",
            "vinfast_care": "Gói VinFast Care Silver: khám ngoại trú 20 triệu/năm, nội trú 200 triệu/năm"
        }
    },
    "VF2026002": {
        "full_name": "Trần Thị Bình",
        "department": "Phòng Nhân sự (HR)",
        "position": "Chuyên viên Tuyển dụng",
        "email": "binh.tt@vinfast.vn",
        "manager": "Lê Thu Hà",
        "annual_leave_total": 12,
        "annual_leave_used": 11,
        "insurance": {
            "social_insurance": "Đang tham gia BHXH bắt buộc (đóng từ 06/2025)",
            "health_insurance": "BHYT — Bệnh viện Vinmec Hải Phòng",
            "vinfast_care": "Gói VinFast Care Standard: khám ngoại trú 10 triệu/năm, nội trú 100 triệu/năm"
        }
    }
}

# Bộ đếm mã đơn nghỉ phép giả lập
_LEAVE_REQUEST_COUNTER = {"value": 100}


def _not_found(employee_id: str) -> str:
    return json.dumps({
        "status": "NOT_FOUND",
        "message": f"Không tìm thấy nhân viên có mã '{employee_id}' trong hệ thống HR VinFast."
    }, ensure_ascii=False)


def execute_leave_balance_query(employee_id: str) -> str:
    """Thực thi tra cứu số ngày phép còn lại theo mã nhân viên"""
    emp = MOCK_DATABASE.get(employee_id.strip().upper())
    if not emp:
        return _not_found(employee_id)
    remaining = emp["annual_leave_total"] - emp["annual_leave_used"]
    return json.dumps({
        "status": "SUCCESS",
        "employee_id": employee_id.strip().upper(),
        "data": {
            "full_name": emp["full_name"],
            "department": emp["department"],
            "position": emp["position"],
            "manager": emp["manager"],
            "annual_leave_total": emp["annual_leave_total"],
            "annual_leave_used": emp["annual_leave_used"],
            "annual_leave_remaining": remaining
        }
    }, ensure_ascii=False)


def execute_insurance_policy_query(employee_id: str) -> str:
    """Thực thi tra cứu chính sách bảo hiểm theo mã nhân viên"""
    emp = MOCK_DATABASE.get(employee_id.strip().upper())
    if not emp:
        return _not_found(employee_id)
    return json.dumps({
        "status": "SUCCESS",
        "employee_id": employee_id.strip().upper(),
        "data": {
            "full_name": emp["full_name"],
            "insurance": emp["insurance"]
        }
    }, ensure_ascii=False)


def _parse_date(date_str: str):
    from datetime import datetime
    return datetime.strptime(date_str.strip(), "%d/%m/%Y")


def execute_create_leave_request(employee_id: str, start_date: str, end_date: str,
                                 leave_type: str = "annual", reason: str = "") -> str:
    """Thực thi tạo đơn xin nghỉ phép (có kiểm tra số ngày phép còn lại)"""
    emp_id = employee_id.strip().upper()
    emp = MOCK_DATABASE.get(emp_id)
    if not emp:
        return _not_found(employee_id)

    try:
        days = (_parse_date(end_date) - _parse_date(start_date)).days + 1
    except ValueError:
        return json.dumps({
            "status": "INVALID_INPUT",
            "message": "Ngày không hợp lệ. Vui lòng dùng định dạng DD/MM/YYYY."
        }, ensure_ascii=False)

    if days <= 0:
        return json.dumps({
            "status": "INVALID_INPUT",
            "message": "Ngày kết thúc phải sau hoặc bằng ngày bắt đầu."
        }, ensure_ascii=False)

    remaining = emp["annual_leave_total"] - emp["annual_leave_used"]
    if leave_type == "annual" and days > remaining:
        return json.dumps({
            "status": "INSUFFICIENT_LEAVE",
            "employee_id": emp_id,
            "requested_days": days,
            "annual_leave_remaining": remaining,
            "message": (f"Nhân viên {emp['full_name']} chỉ còn {remaining} ngày phép năm, "
                        f"không đủ cho {days} ngày xin nghỉ. Có thể chuyển sang nghỉ không lương (unpaid).")
        }, ensure_ascii=False)

    _LEAVE_REQUEST_COUNTER["value"] += 1
    request_id = f"LR-{emp_id}-{_LEAVE_REQUEST_COUNTER['value']}"
    if leave_type == "annual":
        emp["annual_leave_used"] += days

    return json.dumps({
        "status": "SUCCESS",
        "request_id": request_id,
        "employee_id": emp_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "approver": emp["manager"],
        "message": (f"Đã tạo đơn nghỉ phép {request_id} cho {emp['full_name']} ({emp_id}) "
                    f"từ {start_date} đến {end_date} ({days} ngày, loại: {leave_type}). "
                    f"Đơn đang chờ {emp['manager']} phê duyệt.")
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "leave_balance_query": execute_leave_balance_query,
    "insurance_policy_query": execute_insurance_policy_query,
    "create_leave_request": execute_create_leave_request
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
