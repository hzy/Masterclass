from transformers import pipeline, set_seed, GenerationConfig

# Initialize the text generation pipeline with Qwen2.5-3B-Instruct
# device_map="auto" requires 'accelerate', so we rely on default (CPU) or manual setting if needed.
# For a 3B model on CPU, it might be slow but functional.
model_id = "Qwen/Qwen2.5-3B-Instruct"
generator = pipeline("text-generation", model=model_id, trust_remote_code=True)
set_seed(42)

# Manually constructed system prompt for Qwen
history = "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"

print(f"Start chatting with {model_id} (type 'quit' to exit)")

while True:
    try:
        user_input = input(">>> ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # Append user input to history using Qwen's specific chat template format
        # <|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n
        history += f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

        # Create generation config
        generation_config = GenerationConfig(
            max_new_tokens=512,
            pad_token_id=generator.tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        # Generate response
        outputs = generator(history, generation_config=generation_config)

        full_text = outputs[0]["generated_text"]
        # Extract only the newly generated part
        new_text = full_text[len(history) :]

        # Remove the end-of-turn token if present for display
        display_text = new_text.replace("<|im_end|>", "").strip()
        print(display_text)

        # Update history with the full generated text (including <|im_end|> if generated)
        history = full_text
        if not history.endswith("\n"):
            history += "\n"

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
        break
