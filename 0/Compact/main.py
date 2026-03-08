import os
import sys
from mlx_lm import generate, load, stream_generate
from mlx_lm.sample_utils import make_sampler

# Configure parameters
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
MAX_CONTEXT_TOKENS = 64000  # Artificial limit for tutorial purposes
COMPACTION_THRESHOLD = 60000  # Trigger automatic compaction here


def load_novel_text(filename="alice.txt"):
    # Resolve absolute path based on this script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, filename)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'. Please ensure it exists.")
        sys.exit(1)


def count_tokens(messages, tokenizer):
    """Counts tokens in the current message history using the chat template."""
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    # MLX tokenizer behaves similarly to HF tokenizer
    return len(tokenizer.encode(text))


def compact_context(messages, tokenizer, model):
    """
    Compacts the conversation history by summarizing older messages using MLX.
    Preserves the System Prompt (index 0) and the most recent messages.
    """
    print("[System] Compacting context...")

    # Strategy:
    # 0: System Prompt (Keep)
    # 1..-N: History to summarize
    # -N..: Recent history (Keep)

    # If history is too short, nothing to compact
    if len(messages) <= 3:
        print("[System] Not enough history to compact.")
        return messages

    # Keep last 2 exchanges (4 messages) + System Prompt
    msgs_to_keep_count = 2
    if len(messages) <= msgs_to_keep_count + 1:
        print("[System] History too short to compact.")
        return messages

    start_index = 1  # Skip System
    end_index = len(messages) - msgs_to_keep_count

    msgs_to_summarize = messages[start_index:end_index]

    if not msgs_to_summarize:
        print("[System] No messages to summarize.")
        return messages

    # Prepare summary prompt
    summary_prompt = "You are a helpful assistant. Summarize the following conversation history between a User and Alice concisely. Preserve key details."

    conversation_text = ""
    for msg in msgs_to_summarize:
        role = msg["role"]
        content = msg["content"]
        conversation_text += f"{role}: {content}\n"

    summary_messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": conversation_text},
    ]

    # Generate Summary using MLX
    # Apply chat template
    prompt = tokenizer.apply_chat_template(
        summary_messages, tokenize=False, add_generation_prompt=True
    )

    # Generate using mlx_lm
    # Note: mlx_lm.generate handles tokenization internally if prompt is str
    sampler = make_sampler(temp=0.3)
    summary = generate(
        model, tokenizer, prompt=prompt, max_tokens=500, sampler=sampler, verbose=False
    )

    print(f"[System] Summary generated: {summary[:100]}...")

    # Construct new history
    new_messages = [messages[0]]  # System Prompt
    new_messages.append(
        {"role": "system", "content": f"[Previous Conversation Summary]: {summary}"}
    )
    new_messages.extend(messages[end_index:])  # Recent history

    new_count = count_tokens(new_messages, tokenizer)
    print(f"[System] Compaction complete. Context reduced to {new_count} tokens.")

    return new_messages


def main():
    # 1. Initialize Model with MLX
    print(f"Loading {MODEL_NAME} with MLX support (Apple Silicon Optimized)...")
    try:
        # mlx_lm.load returns (model, tokenizer) or (model, tokenizer, config)
        loaded = load(MODEL_NAME, tokenizer_config={"trust_remote_code": True})
        if len(loaded) >= 2:
            model = loaded[0]
            tokenizer = loaded[1]
        else:
            raise ValueError("Unexpected return from mlx_lm.load")

        # Patch tokenizer if needed
        if hasattr(tokenizer, "pad_token") and tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # 2. Prepare System Prompt with Novel
    novel_text = load_novel_text()

    # MLX handles long context much better than PyTorch MPS.
    print(f"Loaded novel text ({len(novel_text)} chars).")

    system_prompt = (
        "You are Alice from Lewis Carroll's 'Alice's Adventures in Wonderland'. "
        "Answer all questions as Alice would, staying in character. "
        "Use the following text as your memory and world knowledge:\n\n"
        f"{novel_text}"
    )

    # Initialize conversation history
    messages = [{"role": "system", "content": system_prompt}]

    # Count initial tokens
    initial_tokens = count_tokens(messages, tokenizer)
    print(f"\nAlice is ready! (Initial Context: {initial_tokens} tokens)")
    print(f"(Context limit: {MAX_CONTEXT_TOKENS} tokens)")
    print("Type '/compact' to manually trigger context compaction.")
    print("Type '/quit' or '/exit' to end the chat.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/quit", "/exit"]:
                print("Alice: Goodbye!")
                break

            # Handle Manual Compaction Command
            if user_input.lower() == "/compact":
                messages = compact_context(messages, tokenizer, model)
                continue

            # Add user message
            messages.append({"role": "user", "content": user_input})

            # Check for Automatic Compaction
            current_tokens = count_tokens(messages, tokenizer)
            if current_tokens > COMPACTION_THRESHOLD:
                print(
                    f"\n[System] Context limit approaching ({current_tokens}/{MAX_CONTEXT_TOKENS}). Auto-compacting..."
                )
                messages = compact_context(messages, tokenizer, model)

            # Generate Response
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            print("Alice: ", end="", flush=True)

            # Stream incremental text chunks from mlx_lm's streaming API.
            response_text = ""
            sampler = make_sampler(temp=0.7)
            for response in stream_generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=512,
                sampler=sampler,
            ):
                if response.text:
                    print(response.text, end="", flush=True)
                    response_text += response.text

            print()  # Newline after response

            # Append assistant response to history
            messages.append({"role": "assistant", "content": response_text})

        except KeyboardInterrupt:
            print("\nAlice: Oh dear, I must be going!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break


if __name__ == "__main__":
    main()
