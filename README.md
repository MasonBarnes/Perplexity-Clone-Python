# Perplexity-Clone-Python
A near perfect replica of Perplexity AI's "Search" function in Python, heavily inspired by [clarity-ai](https://github.com/mckaywrigley/clarity-ai).

## Usage
This Perplexity clone can be easily implemented in Python. Here is an example that can also be found in `example.py`:
```python
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
result = perplexity_clone(prompt, verbose=True)

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
```

## Requirements
Requirements can be installed via the `requirements.txt` file. You will also need an [API key from OpenAI](https://openai.com/product), optionally with GPT-4 if you would like to enable higher-quality completions.
```bash
pip install -r requirements.txt
```

## Credits
Again, huge credit to Mckay Wrigley's [clarity-ai](https://github.com/mckaywrigley/clarity-ai). A lot of the code from this project was ported from his.