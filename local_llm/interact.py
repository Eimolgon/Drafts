from llama_cpp import Llama

llm = Llama(
    model_path="models/Llama-3.2-3B-Instruct-Q3_K_L.gguf",
    n_ctx=4096,
    verbose=False
)

MAX_MESSAGES = 20  # keep last 20 exchanges

messages = []

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    messages.append({"role": "user", "content": user_input})

    # trim old memory
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]

    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=300
    )

    assistant_msg = response["choices"][0]["message"]["content"]

    print("\nAI:", assistant_msg, "\n")

    messages.append({"role": "assistant", "content": assistant_msg})
