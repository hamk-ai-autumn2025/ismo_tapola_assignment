from google import genai
import markdown
from xhtml2pdf import pisa
import os

client = genai.Client()

topic = input("Enter topic for scientific article: ")

prompt = f"""Generate a scientific article on the topic '{topic}' in Markdown format.

The article should have the following structure:
- Abstract
- Introduction
- Main body divided into chapters with subchapters, each with appropriate headings
- Conclusions
- References (in APA style)

Include tables where appropriate.
Use APA style for in-text citations and the reference list.
Ensure the article is comprehensive and follows scientific writing standards.

Output only the Markdown content, no other text."""

response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
markdown_content = response.text.strip()

# Save Markdown to file
with open('scientific_article.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("Markdown article generated and saved as 'scientific_article.md'")

# Convert Markdown to HTML
html = markdown.markdown(markdown_content)

# Generate PDF from HTML
with open('scientific_article.pdf', 'wb') as f:
    pisa.CreatePDF(html, dest=f)
print("PDF generated as 'scientific_article.pdf'")