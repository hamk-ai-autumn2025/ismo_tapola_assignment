import argparse
import sys
import os
from markitdown import MarkItDown
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description='A command line tool to process text, html, csv, docx, or PDF files and query an LLM.')
    parser.add_argument('inputs', nargs='*', help='Input sources: file paths or URLs')
    parser.add_argument('-f', '--file', help='Output file to write the result')
    parser.add_argument('-q', '--query', default='Summarize the following content:', help='Query prompt for the LLM')
    parser.add_argument('-c', '--citations', action='store_true', help='Include citations in the output')
    parser.add_argument('-r', '--reset', action='store_true', help='Reset the input data')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Initialize MarkItDown
    markitdown = MarkItDown()

    # Collect content from all inputs
    combined_content = ""
    for input_source in args.inputs:
        if args.verbose:
            print(f"Processing: {input_source}", file=sys.stderr)
        try:
            if input_source.startswith('http://') or input_source.startswith('https://'):
                # It's a URL
                result = markitdown.convert_url(input_source)
            else:
                # It's a file
                result = markitdown.convert(input_source)
            combined_content += result.text_content + "\n\n"
        except Exception as e:
            print(f"Error processing {input_source}: {e}", file=sys.stderr)
            continue

    if not combined_content.strip():
        print("No content to process.", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI()

    # Prepare the prompt
    prompt = f"{args.query}\n\n{combined_content}"

    if args.citations:
        prompt += "\n\nInclude citations where applicable."

    # Query the LLM
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or gpt-4, depending on preference
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        result = response.choices[0].message.content
    except Exception as e:
        print(f"Error querying LLM: {e}", file=sys.stderr)
        sys.exit(1)

    # Output the result
    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:
            f.write(result)
        if args.verbose:
            print(f"Output written to {args.file}", file=sys.stderr)
    else:
        print(result)

if __name__ == "__main__":
    main()