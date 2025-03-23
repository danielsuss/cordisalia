import os
import re
import yaml

def extract_front_matter(content):
    """Extract YAML front matter from a markdown file."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        try:
            front_matter = yaml.safe_load(match.group(1))
            return front_matter, content[match.end():]
        except yaml.YAMLError:
            return {}, content
    return {}, content

def is_draft(file_path):
    """Check if a file is marked as draft in its front matter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        front_matter, _ = extract_front_matter(content)
        return front_matter.get('draft') == "true"
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def get_markdown_files_by_category():
    """Get all markdown files categorized by directory."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    categories = {}
    
    for root, _, files in os.walk(base_path):
        if root == base_path or os.path.basename(root) == "templates" or "Chapter Notes" in root:
            continue
            
        category = os.path.basename(root)
        if category not in categories:
            categories[category] = []
        
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                if not is_draft(full_path):
                    # Remove the .md extension
                    file_name = file[:-3]
                    categories[category].append(file_name)
    
    return categories

def generate_index_content():
    """Generate the content for index.md."""
    categories = get_markdown_files_by_category()
    
    # Start with the existing header
    content = """---
title: Cordisalia
aliases:
  - Cordisalia
---
Welcome to the world of Cordisalia! Navigate through this wiki using the explorer on the side. ![[World Map.png]]
"""
    
    # Define the order of sections and their titles
    section_order = [
        ("Chapters", "###### Chapters:"),
        ("Characters", "###### Characters:"),
        ("Continents", "###### Continents:"),
        ("Creatures", "###### Creatures:"),
        ("Groups", "###### Groups:"),
        ("Items", "###### Items:"),
        ("Lore", "###### Lore:"),
        ("Points of Interest", "###### Points of Interest:"),
        ("Settlements", "###### Settlements:")
    ]
    
    # Add each section
    for category, header in section_order:
        if category in categories and categories[category]:
            content += f"{header}\n"
            # Sort entries alphabetically
            for item in sorted(categories[category]):
                content += f"- [[{item}]]\n"
            content += "\n"
    
    return content

def update_index():
    """Update the index.md file."""
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.md")
    content = generate_index_content()
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("index.md has been updated successfully!")

if __name__ == "__main__":
    update_index()