import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
import copy

# --- Global Model State ---
model = None
tokenizer = None
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
DEVICE = "mps"  # As requested


def load_model():
    global model, tokenizer
    print(f"Loading model {MODEL_ID} to {DEVICE}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map=DEVICE,
            torch_dtype=torch.float16,
            trust_remote_code=True,
        ).eval()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise e


# --- System Prompt for Tool Calling ---
# Qwen2.5 works well with explicit instructions.
TOOL_SYSTEM_PROMPT = """You are a helpful assistant.
You have access to the following tools:

{tools_json}

To use a tool, please output a JSON object with the "name" and "arguments" keys.
Example: {{"name": "get_weather", "arguments": {{"location": "Beijing"}}}}

If no tool is needed, respond normally.
"""


def prepare_prompt(
    messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Apply chat template and inject tool definitions if needed.
    """
    # Use a copy to avoid modifying the original request
    msgs = copy.deepcopy(messages)

    # 1. Inject System Prompt if tools are present
    if tools:
        # Extract function definitions
        tool_defs = [t.get("function", {}) for t in tools]
        tools_json = json.dumps(tool_defs, indent=2)
        system_content = TOOL_SYSTEM_PROMPT.format(tools_json=tools_json)

        # Check if there is already a system message
        if msgs[0]["role"] == "system":
            msgs[0]["content"] += "\n\n" + system_content
        else:
            msgs.insert(0, {"role": "system", "content": system_content})

    # 2. Apply template
    # Qwen uses ChatML format
    text = tokenizer.apply_chat_template(
        msgs, tokenize=False, add_generation_prompt=True
    )
    return text


async def generate_stream(
    messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Async generator that yields chunks of text from the model.
    """
    if model is None:
        load_model()

    prompt = prepare_prompt(messages, tools)
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        top_p=0.8,
    )

    # Run generation in a separate thread
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    # Simple heuristic to detect JSON output (Tool Call)
    buffer = ""
    is_tool_call = False

    for new_text in streamer:
        # Yield to event loop to keep server responsive
        await asyncio.sleep(0)

        if is_tool_call:
            yield {"type": "tool", "content": new_text}
            continue

        buffer += new_text

        # Heuristic: If it starts with { and has "name", it's likely a tool call
        if len(buffer) > 5:  # minimal check
            stripped = buffer.strip()
            if stripped.startswith("{") and '"name":' in stripped:
                is_tool_call = True
                yield {"type": "tool", "content": buffer}
                buffer = ""  # clear buffer
                continue

        # If buffer gets too long (20 chars) and still not tool call,
        # assume it's content and flush it.
        if len(buffer) > 20:
            yield {"type": "content", "content": buffer}
            buffer = ""

    # Final flush
    if buffer:
        if is_tool_call:
            yield {"type": "tool", "content": buffer}
        else:
            yield {"type": "content", "content": buffer}
