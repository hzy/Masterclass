from transformers import GenerationConfig, pipeline, set_seed

generator = pipeline("text-generation", model="openai-community/gpt2")
set_seed(42)

generation_config = GenerationConfig(
    max_new_tokens=30,
    do_sample=True,
    temperature=0.8,
    pad_token_id=generator.tokenizer.eos_token_id, # The id of the end of sentence token
)
outputs = generator("Hello, I'm a language model,", generation_config=generation_config)
generated_text = outputs[0]["generated_text"]
print(generated_text)
