"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import re
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "",
                            history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu HR thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "",
                            history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        history = history or []
        prompt_lower = prompt.lower()

        # Đã có Observation từ các bước trước -> mô phỏng LLM tổng hợp câu trả lời cuối
        if history:
            last = history[-1]
            obs = last.get("observation", "")
            # Mô phỏng suy luận đa bước: đã tra ngày phép và người dùng muốn tạo đơn -> gọi tiếp create_leave_request
            if last.get("tool_name") == "leave_balance_query" and any(k in prompt_lower for k in ["tạo đơn", "xin nghỉ"]):
                emp_match = re.search(r"vf\d{7}", prompt_lower)
                dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", prompt)
                if '"annual_leave_remaining": 0' in obs or '"annual_leave_remaining": 1,' in obs:
                    return {"type": "text",
                            "content": f"[Mock Agent Response]: Số ngày phép còn lại không đủ ({obs}). Đề xuất nghỉ không lương thay vì tạo đơn phép năm.",
                            "thought": "Observation cho thấy ngày phép không đủ, không tạo đơn."}
                return {"type": "tool_call", "tool_name": "create_leave_request",
                        "arguments": {"employee_id": emp_match.group(0).upper() if emp_match else "VF2026001",
                                      "start_date": dates[0] if dates else "15/09/2026",
                                      "end_date": dates[1] if len(dates) > 1 else (dates[0] if dates else "15/09/2026"),
                                      "leave_type": "annual", "reason": "Việc gia đình"},
                        "thought": "Đã xác nhận đủ ngày phép, tiến hành tạo đơn nghỉ phép."}
            return {"type": "text",
                    "content": f"[Mock Agent Response]: Dựa trên kết quả từ tool '{last.get('tool_name')}': {obs}",
                    "thought": "Đã nhận Observation từ MCP Server, tổng hợp câu trả lời cuối."}

        # Mô phỏng nhận diện intent gọi Tool theo chủ đề HR VinFast
        emp_match = re.search(r"vf\d{7}", prompt_lower)
        emp_id = emp_match.group(0).upper() if emp_match else None

        if emp_id and any(k in prompt_lower for k in ["tạo đơn", "xin nghỉ", "nghỉ phép từ", "đăng ký nghỉ"]):
            dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", prompt)
            start = dates[0] if dates else "15/09/2026"
            end = dates[1] if len(dates) > 1 else start
            return {
                "type": "tool_call",
                "tool_name": "create_leave_request",
                "arguments": {"employee_id": emp_id, "start_date": start, "end_date": end,
                              "leave_type": "annual", "reason": "Việc gia đình"},
                "thought": f"Nhân viên {emp_id} yêu cầu tạo đơn nghỉ phép. Tôi sẽ gọi tool create_leave_request."
            }
        elif emp_id and "bảo hiểm" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "insurance_policy_query",
                "arguments": {"employee_id": emp_id},
                "thought": f"Nhân viên hỏi về gói bảo hiểm của {emp_id}. Tôi sẽ gọi tool insurance_policy_query."
            }
        elif emp_id:
            return {
                "type": "tool_call",
                "tool_name": "leave_balance_query",
                "arguments": {"employee_id": emp_id or "VF2026001"},
                "thought": f"Nhân viên muốn tra cứu số ngày phép còn lại của {emp_id or 'VF2026001'}. Tôi sẽ gọi tool leave_balance_query."
            }
        else:
            return {
                "type": "text",
                "content": "[Mock Agent Response]: Xin chào! Theo chính sách VinFast, nhân viên chính thức có 12 ngày phép năm (tăng 1 ngày sau mỗi 5 năm làm việc) và được tham gia BHXH, BHYT cùng gói bảo hiểm sức khỏe VinFast Care.",
                "thought": "Câu hỏi chung về chính sách nhân sự, trả lời trực tiếp không cần gọi Tool."
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "",
                            history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        history = history or []
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt, history)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            # Dựng lại lịch sử ReAct: user -> (model function_call -> user function_response)*
            contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
            for h in history:
                contents.append(types.Content(role="model", parts=[
                    types.Part(function_call=types.FunctionCall(name=h["tool_name"], args=h.get("arguments", {})))]))
                contents.append(types.Content(role="user", parts=[
                    types.Part(function_response=types.FunctionResponse(
                        name=h["tool_name"], response={"result": h.get("observation", "")}))]))

            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt, history)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "",
                            history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        history = history or []
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt, history)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Dựng lại lịch sử ReAct: assistant tool_call -> tool result (Observation) cho từng bước trước
            for i, h in enumerate(history):
                call_id = h.get("call_id") or f"call_{i + 1}"
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": call_id,
                        "type": "function",
                        "function": {"name": h["tool_name"],
                                     "arguments": json.dumps(h.get("arguments", {}), ensure_ascii=False)}
                    }]
                })
                messages.append({"role": "tool", "tool_call_id": call_id,
                                 "name": h["tool_name"], "content": h.get("observation", "")})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "call_id": call.id,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt, history)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
