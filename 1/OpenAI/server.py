from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import json
import asyncio
import time
from itertools import count
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChunk,
    Choice,
    ChunkChoice,
    ChatMessage,
    Delta,
    ToolCall,
    FunctionCall,
)
import engine


_ID_SEED = f"{time.monotonic_ns():x}"
_ID_COUNTER = count()


def _next_id(prefix: str) -> str:
    return f"{prefix}{_ID_SEED}{next(_ID_COUNTER):x}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    print("Initializing model engine...")
    engine.load_model()
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    print(f"Received request: {request.messages[-1].content}")

    if request.stream:

        async def event_generator():
            chunk_id = _next_id("chatcmpl-")
            model_name = request.model

            # Convert request messages to dicts for engine
            msgs = [m.model_dump(exclude_none=True) for m in request.messages]
            tools = [t for t in request.tools] if request.tools else None

            # Stream from engine
            async for chunk in engine.generate_stream(msgs, tools):
                delta = None
                finish_reason = None

                if chunk["type"] == "tool":
                    # For simplicity, we stream tool content as function arguments
                    # In a real implementation, you'd need to parse the JSON structure
                    # Here we assume the entire content is the arguments JSON
                    delta = Delta(
                        tool_calls=[
                            ToolCall(
                                index=0,
                                function=FunctionCall(arguments=chunk["content"]),
                            )
                        ]
                    )
                else:
                    delta = Delta(content=chunk["content"])

                response_chunk = ChatCompletionChunk(
                    id=chunk_id,
                    model=model_name,
                    choices=[ChunkChoice(index=0, delta=delta, finish_reason=None)],
                )
                yield f"data: {response_chunk.model_dump_json(exclude_unset=True)}\n\n"

            # Final chunk
            yield f"data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    else:
        # Non-streaming implementation (simplified, just consume the stream)
        # In production, use generate() without streamer
        full_content = ""
        is_tool = False
        msgs = [m.model_dump(exclude_none=True) for m in request.messages]
        tools = [t for t in request.tools] if request.tools else None

        async for chunk in engine.generate_stream(msgs, tools):
            full_content += chunk["content"]
            if chunk["type"] == "tool":
                is_tool = True

        if is_tool:
            # Try to parse the accumulated JSON
            try:
                tool_data = json.loads(full_content)
                tool_calls = [
                    {
                        "id": _next_id("call_"),
                        "type": "function",
                        "function": {
                            "name": tool_data.get("name"),
                            "arguments": json.dumps(tool_data.get("arguments")),
                        },
                    }
                ]
                message = ChatMessage(role="assistant", tool_calls=tool_calls)
                finish_reason = "tool_calls"
            except:
                # Fallback if parsing fails
                message = ChatMessage(role="assistant", content=full_content)
                finish_reason = "stop"
        else:
            message = ChatMessage(role="assistant", content=full_content)
            finish_reason = "stop"

        return ChatCompletionResponse(
            model=request.model,
            choices=[Choice(index=0, message=message, finish_reason=finish_reason)],
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
