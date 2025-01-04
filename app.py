import json
import os
from bs4 import BeautifulSoup
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

# Get the directory where the Python script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Function to load tags from the JSON file
def load_tags():
    tags_file_path = os.path.join(BASE_DIR, 'tags.json')  # Construct the full path
    with open(tags_file_path) as f:
        data = json.load(f)
        return data.get("tags", [])

# Function to recursively print HTML elements and highlight specified tags
def print_element_hierarchy(element, indent=0):
    indent_str = "&nbsp;&nbsp;&nbsp;&nbsp;" * indent
    
    # Color coding based on common element types
    tag_color = {
        "div": "#4CAF50",  # Green for divs
        "h1": "#FF5722",   # Orange for headings
        "p": "#3F51B5",    # Blue for paragraphs
        "a": "#009688",    # Teal for links
        "span": "#E91E63", # Pink for spans
        "svg": "#8E44AD",  # Purple for SVGs
        # Add more color codes for different tags
    }
    
    # Apply color to the tag name based on its type
    color = tag_color.get(element.name, "#000")  # Default to black if not in dict
    tag_info = f"{indent_str}<span style='color:{color};'>&lt;{element.name}&gt;</span>"
    
    # Display attributes more clearly
    attributes = []
    if element.get('id'):
        attributes.append(f"id='{element['id']}'")
    if element.get('class'):
        attributes.append(f"class='{' '.join(element['class'])}'")
    if element.get('name'):
        attributes.append(f"name='{element['name']}'")

    if attributes:
        tag_info += f" <span class='attributes'>({', '.join(attributes)})</span>"

    result = tag_info + "<br>"

    # Recursive call for each child element.
    children = list(element.find_all(recursive=False))
    if children:
        for child in children:
            result += print_element_hierarchy(child, indent + 1)

    # Closing tag is aligned properly
    result += f"{indent_str}<span style='color:{color};'>&lt;/{element.name}&gt;</span><br>"
    
    return result


@app.route('/', methods=['GET', 'POST'])
def home():
    structure = None
    interesting_tags = None
    if request.method == 'POST':
        url = request.form['url']
        selected_tags = request.form.getlist('tags')  # Get selected tags

        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            body = soup.body
            if body:
                structure = print_element_hierarchy(body)
            else:
                structure = "&lt;body&gt; tag not found in the provided URL."
            
            # Show only the tags that were selected
            if selected_tags:
                interesting_tags = ""
                for tag in selected_tags:
                    elements = soup.find_all(tag)
                    if elements:
                        interesting_tags += f"Elements for tag &lt;{tag}&gt;:<br>"
                        for elem in elements:
                            interesting_tags += print_element_hierarchy(elem) + "<br>"
            else:
                interesting_tags = None  # Do not display the section if no tags are selected
        except requests.exceptions.RequestException as e:
            structure = f"Error fetching the URL: {e}"

    return render_template('index.html', structure=structure, interesting_tags=interesting_tags, tags=load_tags())

if __name__ == "__main__":
    app.run(debug=True)
