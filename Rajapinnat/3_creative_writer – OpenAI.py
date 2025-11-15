import os
from openai import OpenAI

def generate_creative_content(prompt, model, temperature, top_p, presence_penalty, frequency_penalty):
    """
    Generates creative content using the OpenAI API with specific parameters.
    """
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        system_prompt = (
            "You are a creative writer, an expert in crafting compelling and SEO-optimized content. "
            "Your task is to generate a piece of content based on the user's prompt. "
            "The content should be engaging, original, and tailored for search engine visibility. "
            "To achieve this, you must use a rich vocabulary and a wide variety of synonyms for common words. "
            "Avoid repetition and clichés. Think outside the box and come up with unique angles and ideas. "
            "The final output should be a polished piece of content ready for publication."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {e}"

def main():
    """
    Main function to run an interactive loop for content generation.
    """
    # Define different configurations for content generation
    configs = [
        {"temperature": 0.7, "top_p": 0.9, "presence_penalty": 0.5, "frequency_penalty": 0.5},
        {"temperature": 0.9, "top_p": 1.0, "presence_penalty": 0.2, "frequency_penalty": 0.2},
        {"temperature": 0.5, "top_p": 0.8, "presence_penalty": 0.8, "frequency_penalty": 0.8},
    ]

    model = "gpt-3.5-turbo"

    while True:
        prompt = input("Enter a subject (or 'quit'/'exit' to stop): ")
        if prompt.lower() in ["quit", "exit"]:
            break

        print(f"Generating content for prompt: '{prompt}'\n")

        for i, config in enumerate(configs):
            print(f"--- Version {i+1} ---")
            content = generate_creative_content(
                prompt=prompt,
                model=model,
                temperature=config["temperature"],
                top_p=config["top_p"],
                presence_penalty=config["presence_penalty"],
                frequency_penalty=config["frequency_penalty"],
            )
            print(content)
            print("\n")

if __name__ == "__main__":
    main()
