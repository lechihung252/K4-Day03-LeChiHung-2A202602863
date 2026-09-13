# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Lê Chí Hùng  
> **Mã Sinh Viên / Mã Học viên:** 2A202602863
> **Chủ đề Lựa chọn:** *Trợ lý Nhân sự VinFast (HR Assistant):* Tra cứu ngày phép còn lại, chính sách bảo hiểm và tạo đơn xin nghỉ phép. 

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Tình huống "xin nghỉ phép" buộc agent phải chia nhỏ: (1) xác định mã nhân viên → (2) tra cứu số ngày phép còn lại → (3) so sánh với số ngày muốn nghỉ → (4) kiểm tra chính sách (ví dụ nghỉ ốm cần giấy BHXH) → (5) mới tạo đơn. Không đạt 5 vì chuỗi suy luận tương đối tuyến tính, ít nhánh rẽ phức tạp. |
| **2. Tool Interaction** | 5 / 5 | Không thể trả lời từ System Prompt: số ngày phép, hồ sơ bảo hiểm là dữ liệu cá nhân thay đổi theo thời gian, phải gọi MCP tool leave_balance_query / insurance_policy_query; tạo đơn là hành động ghi vào hệ thống (create_leave_request), không chỉ đọc. |
| **3. Dynamic Decision** | 4 / 5 | Bước tiếp theo phụ thuộc kết quả quan sát: nếu remaining_days < số ngày xin → từ chối / đề xuất nghỉ không lương thay vì tạo đơn; nếu tool trả NOT_FOUND (mã NV sai) → hỏi lại thay vì bịa. Kết quả tool quyết định rẽ nhánh, nhưng số nhánh còn hạn chế. |
| **4. Long Horizon Goal** | 4 / 5 | Agent phải giữ mục tiêu "hoàn tất đơn nghỉ phép" xuyên suốt nhiều lượt: hỏi thiếu thông tin (ngày bắt đầu, lý do), gặp lỗi phải tra lại, vẫn phải nhớ ý định gốc và mã nhân viên đã cung cấp. Chưa đạt 5 vì phiên hội thoại thường ngắn (vài lượt), không kéo dài hàng chục bước như agent lập kế hoạch dài hạn. |
| **TỔNG ĐIỂM AGENTIC FIT** | **17 / 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

> 🔌 **Cấu hình nghiệm thu:** `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini` (OpenAI API thật) · MCP Server: `vinfast-hr-mcp-server` · 5/5 Test Cases · 10 sự kiện trace · 5 lượt gọi Tool qua MCP.

**TC03 — Tạo đơn nghỉ phép (3 bước ReAct: tra ngày phép → tạo đơn → Final Answer):**

```json
[
  {
    "step": 1,
    "query": "Tạo đơn xin nghỉ phép năm cho nhân viên VF2026001 từ ngày 15/09/2026 đến ngày 17/09/2026, lý do việc gia đình.",
    "action_type": "TOOL_EXECUTION",
    "thought": "OpenAI quyết định gọi công cụ 'leave_balance_query' với tham số: {\"employee_id\": \"VF2026001\"}",
    "tool_name": "leave_balance_query",
    "arguments": {
      "employee_id": "VF2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "employee_id": "VF2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "department": "Phòng Kỹ thuật Pin (Battery Engineering)",
        "position": "Kỹ sư Phần mềm",
        "manager": "Trần Minh Quân",
        "annual_leave_total": 15,
        "annual_leave_used": 6,
        "annual_leave_remaining": 9
      }
    },
    "latency_ms": 1198.6
  },
  {
    "step": 2,
    "query": "Tạo đơn xin nghỉ phép năm cho nhân viên VF2026001 từ ngày 15/09/2026 đến ngày 17/09/2026, lý do việc gia đình.",
    "action_type": "TOOL_EXECUTION",
    "thought": "OpenAI quyết định gọi công cụ 'create_leave_request' với tham số: {\"employee_id\": \"VF2026001\", \"start_date\": \"15/09/2026\", \"end_date\": \"17/09/2026\", \"leave_type\": \"annual\", \"reason\": \"việc gia đình\"}",
    "tool_name": "create_leave_request",
    "arguments": {
      "employee_id": "VF2026001",
      "start_date": "15/09/2026",
      "end_date": "17/09/2026",
      "leave_type": "annual",
      "reason": "việc gia đình"
    },
    "observation": {
      "status": "SUCCESS",
      "request_id": "LR-VF2026001-101",
      "employee_id": "VF2026001",
      "leave_type": "annual",
      "start_date": "15/09/2026",
      "end_date": "17/09/2026",
      "days": 3,
      "approver": "Trần Minh Quân",
      "message": "Đã tạo đơn nghỉ phép LR-VF2026001-101 cho Nguyễn Văn An (VF2026001) từ 15/09/2026 đến 17/09/2026 (3 ngày, loại: annual). Đơn đang chờ Trần Minh Quân phê duyệt."
    },
    "latency_ms": 907.76
  },
  {
    "step": 3,
    "query": "Tạo đơn xin nghỉ phép năm cho nhân viên VF2026001 từ ngày 15/09/2026 đến ngày 17/09/2026, lý do việc gia đình.",
    "action_type": "FINAL_ANSWER",
    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Đơn xin nghỉ phép năm đã được tạo thành công cho nhân viên Nguyễn Văn An (mã nhân viên: VF2026001) với thông tin như sau:\n\n- **Thời gian nghỉ**: từ 15/09/2026 đến 17/09/2026 (3 ngày)\n- **Lý do**: việc gia đình\n- **Trạng thái**: Đơn đang chờ phê duyệt từ quản lý Trần Minh Quân.\n\nMã đơn xin nghỉ phép: **LR-VF2026001-101**. \n\nNếu cần thêm thông tin gì, bạn hãy cho tôi biết nhé!",
    "latency_ms": 1532.21
  }
]
```

**TC04 — Suy luận đa bước có rẽ nhánh (Agent tra ngày phép, thấy chỉ còn 1 ngày nên chủ động KHÔNG tạo đơn):**

```json
[
  {
    "step": 1,
    "query": "Nhân viên VF2026002 muốn xin nghỉ phép năm 5 ngày từ 21/09/2026 đến 25/09/2026. Hãy kiểm tra xem còn đủ ngày phép không rồi mới tạo đơn giúp tôi.",
    "action_type": "TOOL_EXECUTION",
    "thought": "OpenAI quyết định gọi công cụ 'leave_balance_query' với tham số: {\"employee_id\": \"VF2026002\"}",
    "tool_name": "leave_balance_query",
    "arguments": {
      "employee_id": "VF2026002"
    },
    "observation": {
      "status": "SUCCESS",
      "employee_id": "VF2026002",
      "data": {
        "full_name": "Trần Thị Bình",
        "department": "Phòng Nhân sự (HR)",
        "position": "Chuyên viên Tuyển dụng",
        "manager": "Lê Thu Hà",
        "annual_leave_total": 12,
        "annual_leave_used": 11,
        "annual_leave_remaining": 1
      }
    },
    "latency_ms": 818.24
  },
  {
    "step": 2,
    "query": "Nhân viên VF2026002 muốn xin nghỉ phép năm 5 ngày từ 21/09/2026 đến 25/09/2026. Hãy kiểm tra xem còn đủ ngày phép không rồi mới tạo đơn giúp tôi.",
    "action_type": "FINAL_ANSWER",
    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Nhân viên Trần Thị Bình (mã nhân viên VF2026002) còn lại 1 ngày phép năm. Vì yêu cầu nghỉ phép 5 ngày từ 21/09/2026 đến 25/09/2026, nhân viên không đủ ngày phép để nghỉ.\n\nNếu bạn vẫn muốn xin nghỉ, tôi có thể tạo đơn nghỉ không lương cho 5 ngày này. Bạn có muốn tiếp tục không?",
    "latency_ms": 1199.43
  }
]
```

**Nhận xét quan sát (Observation):**
- Agent tự quyết định số bước: TC01 trả lời trực tiếp không gọi Tool (1 bước); TC02/TC05 gọi 1 Tool rồi tổng hợp (2 bước); TC03 gọi 2 Tool liên tiếp (3 bước).
- Ở TC03, dù người dùng chỉ yêu cầu "tạo đơn", Agent vẫn chủ động gọi `leave_balance_query` trước để kiểm tra, đúng quy tắc 4 trong System Prompt.
- Ở TC04, Observation `annual_leave_remaining = 1` khiến Agent rẽ nhánh: không gọi `create_leave_request` mà trả lời từ chối và đề xuất phương án khác (Dynamic Decision).
- Ở TC05, Tool trả `NOT_FOUND`, Agent không bịa dữ liệu mà đề nghị kiểm tra lại mã nhân viên (Anti-Hallucination).

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (OpenAI `gpt-4o-mini`).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt (TC02: 1, TC03: 2, TC04: 1, TC05: 1; TC01 không gọi Tool).
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
