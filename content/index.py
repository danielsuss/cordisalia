#!/usr/bin/env python3
"""
This script updates the Cordisalia wiki index.md file by:
1. Finding chapter files in the Chapters directory and updating the chapter list
2. Clearing the "Recently Added / Updated" section
3. Finding the 5 most recently created files that aren't drafts, chapters, templates, or in root
4. Finding the 5 most recently modified files that aren't drafts, chapters, templates, or in root
5. Updating the "Recently Added / Updated" section with wiki-style links to these files
"""

import os
import re
import glob
from datetime import datetime
import frontmatter

def get_chapter_files():
    """Get all chapter files in the Chapters directory sorted by chapter number."""
    # Look for chapter files in the Chapters directory
    chapter_dir = os.path.join(".", "Chapters")
    if not os.path.exists(chapter_dir):
        return []  # Return empty list if Chapters directory doesn't exist
    
    chapter_files = glob.glob(os.path.join(chapter_dir, "Chapter*.md"))
    
    # Sort chapters by number
    def extract_chapter_number(filename):
        # Extract the chapter number, handling both simple numbers and decimals
        match = re.search(r'Chapter (\d+(?:\.\d+)?)', filename)
        if match:
            chapter_str = match.group(1)
            # Convert to float for proper sorting of decimal chapters
            return float(chapter_str)
        return 0
    
    return sorted(chapter_files, key=extract_chapter_number)

def get_file_creation_date(file_path):
    """Get file creation date."""
    try:
        # Some operating systems store creation date differently
        # This is the Windows and macOS way
        return os.path.getctime(file_path)
    except:
        # Fallback to modification time if creation time is not available
        return os.path.getmtime(file_path)

def get_file_modification_date(file_path):
    """Get file modification date."""
    return os.path.getmtime(file_path)

def is_draft(file_path):
    """Check if file is marked as draft in frontmatter."""
    try:
        post = frontmatter.load(file_path)
        return post.get('draft', "").lower() == 'true'
    except Exception:
        # If the file can't be parsed, assume it's not a draft
        return False

def should_include_in_recent(file_path):
    """Determine if a file should be included in the recent files list."""
    # Exclude files in the root directory
    if os.path.dirname(file_path) == '.' or os.path.dirname(file_path) == '':
        return False
    
    # Exclude files in the Chapters directory
    if os.path.dirname(file_path).endswith('Chapters'):
        return False
    
    # Exclude files in the templates directory
    if 'templates' in os.path.dirname(file_path).lower():
        return False
    
    # Exclude draft files
    if is_draft(file_path):
        return False
    
    # Only include markdown files
    if not file_path.endswith('.md'):
        return False
    
    return True

def get_files_for_recent_section():
    """Get files eligible for the recently updated section."""
    eligible_files = []
    for root, dirs, files in os.walk('.'):
        # Skip the root directory itself
        if root == '.':
            continue
            
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                if should_include_in_recent(full_path):
                    eligible_files.append(full_path)
    
    return eligible_files

def format_wiki_link(file_path):
    """Format a file path as an Obsidian-style wiki link."""
    # Remove the extension and only get the filename without path
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    # Obsidian style uses just the filename in double brackets
    return f"[[{file_name}]]"

def update_index_file():
    # Read the current index.md file
    with open("index.md", "r", encoding="utf-8") as file:
        content = file.read()
    
    # Extract sections without removing existing content
    header_match = re.match(r'# Welcome to the World of Cordisalia\s*?!?\[\[World Map\.png\]\]', content)
    header = "# Welcome to the World of Cordisalia\n![[World Map.png]]" if not header_match else header_match.group(0)
    
    # Get the explore section exactly as it is
    explore_section_match = re.search(r'(## Explore By Category[\s\S]*?)## Recently Added / Updated', content)
    explore_section = explore_section_match.group(1).strip() if explore_section_match else "## Explore By Category\n- [Characters](https://cordisalia.pages.dev/Characters/)\n- [Creatures](https://cordisalia.pages.dev/Creatures/)\n- [Groups](https://cordisalia.pages.dev/Groups/)\n- [Continents](https://cordisalia.pages.dev/Continents/)\n- [Settlements](https://cordisalia.pages.dev/Settlements/)\n- [Points of Interest](https://cordisalia.pages.dev/Points-of-Interest/)\n- [Lore](https://cordisalia.pages.dev/Lore/)\n- [Items](https://cordisalia.pages.dev/Items/)"
    
    # 1. Update chapter list
    chapter_files = get_chapter_files()
    chapter_list = "\n".join([f"- [[{os.path.splitext(os.path.basename(chapter))[0]}]]" for chapter in chapter_files])
    
    # Get eligible files for the recently updated section
    eligible_files = get_files_for_recent_section()
    
    # 2 & 3. Find 5 most recently created files
    created_files = sorted(eligible_files, key=get_file_creation_date, reverse=True)[:5]
    
    # 4. Find 5 most recently modified files (excluding those in created_files)
    modified_files = []
    for file in sorted(eligible_files, key=get_file_modification_date, reverse=True):
        if file not in created_files and len(modified_files) < 5:
            modified_files.append(file)
    
    # 5. Create the recently updated section with a single list (no subheadings)
    all_recent_files = created_files + modified_files
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recent_files = []
    for file in all_recent_files:
        if file not in seen:
            seen.add(file)
            unique_recent_files.append(file)
    
    recently_updated = "\n"
    if unique_recent_files:
        recently_updated += "\n".join([f"- {format_wiki_link(file)}" for file in unique_recent_files])
    else:
        recently_updated += "No recently updated files found."
    
    # Assemble the updated index.md content
    updated_content = (
        f"{header}\n## Story Chapters\n{chapter_list}\n"
        f"{explore_section}\n## Recently Added / Updated{recently_updated}\n"
    )
    
    # Write the updated content back to index.md
    with open("index.md", "w", encoding="utf-8") as file:
        file.write(updated_content)
    
    print(f"Updated index.md with {len(chapter_files)} chapters and {len(unique_recent_files)} recently updated files.")

if __name__ == "__main__":
    update_index_file()