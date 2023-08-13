from perpclone import perplexity_clone
import webbrowser
import markdown
import tempfile
import openai

# Ask for the API key
openai.api_key = input("Enter your OpenAI API key: ")

# Ask for the prompt
prompt = input("Enter a prompt: ")

# Send the prompt to the perplexity_clone function
result = perplexity_clone(
    prompt,
    verbose=True
)

# Convert the result to HTML and add the prompt as a header
html = f"<h1>{prompt}</h1>" + markdown.markdown(result.replace("\n", "<br>"))

# Add CSS to the HTML content
html = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 20px;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>
"""

# Save the HTML to a temporary file
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
    url = "file://" + f.name
    f.write(html)

# Open the HTML file in the browser
webbrowser.open(url)