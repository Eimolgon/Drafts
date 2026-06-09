from llama_cpp import Llama

# Load model
llm = Llama(
    model_path="models/Llama-3.2-3B-Instruct-Q3_K_L.gguf",
    n_ctx=2048,
    verbose=False
)

# Ask a question
response = llm.create_chat_completion(
    messages=[
        {
            "role": "user",
            "content": "What is Newton's third law?"
        }
    ],
    max_tokens=200
)

print(response["choices"][0]["message"]["content"])
