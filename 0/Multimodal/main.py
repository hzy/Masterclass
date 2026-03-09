import torch
from transformers import AutoProcessor
from transformers import Qwen2_5_VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
from PIL import Image
import os
import requests


def get_image(path_or_url="https://http.cat/images/404.jpg", local_path="example.jpg"):
    if os.path.exists(local_path):
        return local_path

    if path_or_url.startswith("http"):
        print(f"Downloading image from {path_or_url}...")
        try:
            response = requests.get(path_or_url, stream=True)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Saved image to {local_path}")
            return local_path
        except Exception as e:
            print(f"Failed to download image: {e}")
            # Fallback to dummy image
            print("Creating dummy image instead.")

    # Create a simple red square image as fallback
    img = Image.new("RGB", (256, 256), color="red")
    img.save(local_path)
    print(f"Created dummy image at {local_path}")
    return local_path


def main():
    # 1. Setup
    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    image_path = get_image()

    print(f"Loading model processor: {model_id}...")
    # We only need the processor to demonstrate the ChatML formatting
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    # 2. Define the Multimodal Input
    # This is the "High Level" representation
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_path,
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ]

    print("\n=== 1. High-Level Input (Messages) ===")
    print(messages)

    # 3. ChatML Formatting (The "Reflection")
    # We use apply_chat_template to see what the model actually receives as text/structure.
    # CRITICAL CONCEPT: In the ChatML text string, the image is represented by a
    # SINGLE block: <|vision_start|><|image_pad|><|vision_end|>
    # This is the "placeholder" that tells the processor where to inject the visual tokens later.

    prompt_text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    print("\n=== 2. ChatML Prompt (Text Representation) ===")
    print(
        "Notice that the image is represented as a single placeholder block in the text:"
    )
    print("-" * 40)
    print(prompt_text)
    print("-" * 40)

    # 4. Tokenization (The "Real" Input)
    # The image is not just text tags; it becomes pixel values and image tokens.
    # Qwen2.5-VL uses "Dynamic Resolution". The processor analyzes the image size/aspect ratio
    # and splits it into a variable number of patches.
    # It then EXPANDS that single <|image_pad|> from step 2 into MANY <|image_pad|> tokens.

    print("Now the processor expands the image into actual visual tokens...")
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[prompt_text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )

    input_ids = inputs.input_ids
    pixel_values = inputs.pixel_values

    print(f"Input IDs shape: {input_ids.shape} (Text + Visual Tokens)")
    print(f"Pixel Values shape: {pixel_values.shape} (Raw Image Patches)")
    print(f"Image Grid Thw shape: {inputs.image_grid_thw} (Dynamic Grid Info)")

    # Let's count the image tokens
    # Qwen2.5-VL uses <|image_pad|> (token id 151655 usually) to represent image patches
    # We can inspect the tokens to see how many pad tokens were inserted

    # Note: The exact token ID might vary, usually it's defined in processor.image_token_id or similar,
    # but for Qwen-VL it's often implicit in the pixel_values handling or explicit tokens.
    # Let's just decode the tokens back to text to see the structure with special tokens preserved.

    decoded_text = processor.batch_decode(input_ids, skip_special_tokens=False)[0]
    print("\n=== 4. Decoded Tokens (Verifying input structure) ===")
    # Truncate if too long (image tokens might be many)
    # Qwen2.5-VL represents images as <|vision_start|><|image_pad|>...<|image_pad|><|vision_end|>

    if len(decoded_text) > 100000:
        print(f"Total length: {len(decoded_text)} chars. Showing start and end...")
        print(decoded_text[:500] + "\n...[IMAGE TOKENS]...\n" + decoded_text[-200:])
    else:
        print(decoded_text)

    # 5. Model Forward
    # Uncomment below to run inference if GPU/Model is available.

    print("\n=== 5. Running Inference (Loading Model...) ===")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto"
    )
    # Move inputs to the same device as model
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    print("Generating...")
    generated_ids = model.generate(**inputs, max_new_tokens=128)
    output_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(f"\nModel Output: {output_text}")


if __name__ == "__main__":
    main()
