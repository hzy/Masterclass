import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. 初始化模型 (使用 Apple Silicon 的 MPS 加速)
model_name = "Qwen/Qwen2.5-3B-Instruct"
print(f"正在加载 {model_name}，调用 Apple Silicon MPS 硬件加速...")

# 关键：device_map="mps" 启用 Mac GPU 加速，torch_dtype=torch.float16 节省内存
tokenizer = AutoTokenizer.from_pretrained(model_name)
# 补丁：解决 pad_token 可能未定义导致 attention_mask 警告的问题
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map="mps", torch_dtype=torch.float16
)


# 2. 定义我们的 Tool (这里模拟一个查天气的本地函数)
def get_weather(city: str) -> str:
    print(f"\n[本地系统] 🔧 正在执行工具: get_weather, 参数: {city}")
    weather_db = {"Beijing": "Sunny, 25°C", "London": "Rainy, 15°C"}
    return weather_db.get(city, "Weather data not found.")


# 3. 提供给模型的“工具说明书” (标准 JSON Schema 格式)
tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g., Beijing, London",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


# 4. 核心对话逻辑
def run_modern_tool_calling(user_query):
    print(f"\n👨‍💻 用户: {user_query}")

    # 构造对话历史
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_query},
    ]

    # 第一步：让模型决定是否调用工具
    # transformers 现代版本支持直接传入 tools，它会自动将其拼接到 prompt 中
    text = tokenizer.apply_chat_template(
        messages, tools=tools_definition, add_generation_prompt=True, tokenize=False
    )

    inputs = tokenizer(text, return_tensors="pt").to("mps")

    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.1,  # 依然保持低温度，保证工具调用的稳定性
    )

    response_text = tokenizer.decode(
        outputs[0][len(inputs.input_ids[0]) :], skip_special_tokens=True
    )

    # 解析模型的初步输出
    # Qwen2.5 触发工具时，会输出类似: {"name": "get_weather", "arguments": {"city": "London"}}
    try:
        # 尝试将模型输出解析为 JSON，检查是否发起了工具调用
        if "{" in response_text and "}" in response_text:
            # 提取 JSON 块
            json_str = response_text[
                response_text.find("{") : response_text.rfind("}") + 1
            ]
            tool_call = json.loads(json_str)

            if "name" in tool_call and tool_call["name"] == "get_weather":
                city = tool_call["arguments"]["city"]
                print(f"🤖 模型请求调用工具: {tool_call['name']}, 参数: {city}")

                # 第二步：执行本地 Python 函数
                observation = get_weather(city)
                print(f"[本地系统] 🔧 工具执行结果: {observation}")

                # 第三步：将结果反馈给模型
                messages.append(
                    {"role": "assistant", "content": response_text}
                )  # 记录模型的调用动作
                messages.append(
                    {"role": "tool", "name": "get_weather", "content": observation}
                )  # 传入工具结果

                # 让模型根据工具结果生成最终回答
                final_text = tokenizer.apply_chat_template(
                    messages, add_generation_prompt=True, tokenize=False
                )
                final_inputs = tokenizer(final_text, return_tensors="pt").to("mps")
                final_outputs = model.generate(
                    **final_inputs, max_new_tokens=100, temperature=0.7
                )
                final_answer = tokenizer.decode(
                    final_outputs[0][len(final_inputs.input_ids[0]) :],
                    skip_special_tokens=True,
                )
                print(f"\n🤖 最终回答: {final_answer}")
                return
    except Exception as e:
        pass

    # 如果没有触发工具调用，或者解析失败，直接打印模型回答
    print(f"\n🤖 直接回答 (未使用工具): {response_text}")


# 5. 测试
if __name__ == "__main__":
    run_modern_tool_calling("What's the weather like in Beijing today?")
