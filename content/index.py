#!/usr/bin/env python3
"""
This script updates the Cordisalia wiki index.md file by:
1. Finding chapter files in the Chapters directory and updating the chapter list
2. Clearing the "Recently Added / Updated" section
3. Finding the 5 most recently created files that aren't drafts, chapters, templates, or in root
4. Finding the 5 most recently modified files that aren't drafts, chapters, templates, or in root
5. Updating the "Recently Added / Updated" section with wiki-style links to these files
6. Collecting all unique image links from non-draft files (excluding specific directories)
7. Creating a 3-column table of random images at the bottom of the index file
"""

import os
import re
import glob
import random
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

def should_exclude_directory(directory):
    """Check if this directory should be excluded from processing."""
    excluded_dirs = [
        'Chapters', 
        'Chapter Notes', 
        'Continents', 
        'Misc. Notes', 
        'Statblocks', 
        'templates'
    ]
    
    # Check if directory path contains any of the excluded directory names
    for excluded_dir in excluded_dirs:
        if excluded_dir in directory:
            return True
    return False

def should_include_in_recent(file_path):
    """Determine if a file should be included in the recent files list."""
    # Exclude files in the root directory
    if os.path.dirname(file_path) == '.' or os.path.dirname(file_path) == '':
        return False
    
    # Check if file is in any excluded directory
    if should_exclude_directory(os.path.dirname(file_path)):
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

def extract_note_title_from_path(file_path):
    """Extract the note title from the file path where the image was found."""
    # Get directory and file name without extension
    dir_name = os.path.dirname(file_path) if os.path.dirname(file_path) else "Root"
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Use the file name as the note title
    return file_name

def collect_image_links_with_context():
    """
    Collect unique image links from non-draft files, excluding specific directories.
    Returns a randomized list of image links with their source file information.
    Prevents duplicates based on image filename.
    """
    # Dictionary to track images by filename
    unique_images = {}
    
    for root, dirs, files in os.walk('.'):
        # Skip the root directory and excluded directories
        if root == '.' or should_exclude_directory(root):
            continue
            
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                # Skip draft files
                if is_draft(file_path):
                    continue
                
                # Read the file and search for image links
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find all image links using regex
                    # Pattern matches ![[image.extension]] format
                    image_link_pattern = r'!\[\[(.*?)\]\]'
                    links = re.findall(image_link_pattern, content)
                    
                    # Get the note title for context
                    note_title = extract_note_title_from_path(file_path)
                    
                    # Add links to the dictionary, using image name as key to prevent duplicates
                    for link in links:
                        # Use the image filename as the key to prevent duplicates
                        if link not in unique_images:
                            unique_images[link] = (link, note_title)
                            
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    # Convert dictionary values to list
    image_links_with_context = list(unique_images.values())
    
    # Randomize the list
    random.shuffle(image_links_with_context)
    
    return image_links_with_context

def create_gallery_table(image_links_with_context, columns=3):
    """
    Create a markdown table with the given image links distributed across columns.
    
    Args:
        image_links_with_context: List of tuples (image_name, note_title)
        columns: Number of columns in the table
    
    Returns:
        A formatted markdown table as a string
    """
    if not image_links_with_context:
        return "No images found to create gallery."
    
    # Initialize table
    table = "| | | |\n"
    table += "|---|---|---|\n"
    
    # Calculate how many rows we need
    rows = (len(image_links_with_context) + columns - 1) // columns
    
    # Create each row
    for row in range(rows):
        row_content = "|"
        for col in range(columns):
            idx = row * columns + col
            if idx < len(image_links_with_context):
                img_name, note_title = image_links_with_context[idx]
                # Format as [![[image.png]]](<Title of note>)
                formatted_link = f"[![[{img_name}]]](<{note_title}>)"
                row_content += f" {formatted_link} |"
            else:
                row_content += " |"
        table += row_content + "\n"
    
    return table

def update_index_file():
    # Read the current index.md file
    index_exists = os.path.exists("index.md")
    
    if index_exists:
        with open("index.md", "r", encoding="utf-8") as file:
            content = file.read()
            
        # Try to load existing frontmatter
        try:
            post = frontmatter.loads(content)
            existing_frontmatter = dict(post)
            # Update the content to exclude frontmatter
            content = post.content
        except:
            existing_frontmatter = {}
    else:
        content = ""
        existing_frontmatter = {}
    
    # Ensure title is set to "Cordisalia"
    existing_frontmatter['title'] = "Cordisalia"
    
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
    
    # Collect image links for the gallery
    image_links_with_context = collect_image_links_with_context()
    
    # Create the image gallery
    gallery_table = create_gallery_table(image_links_with_context)
    
    # Assemble the updated index.md content
    updated_content = (
        f"{header}\n## Story Chapters\n{chapter_list}\n"
        f"{explore_section}\n## Recently Added / Updated{recently_updated}\n"
        f"## Gallery\n{gallery_table}"
    )
    
    # Create a new post with frontmatter and content
    post = frontmatter.Post(updated_content, **existing_frontmatter)
    
    # Write the updated content back to index.md
    with open("index.md", "w", encoding="utf-8") as file:
        file.write(frontmatter.dumps(post))
    
    print(f"Updated index.md with {len(chapter_files)} chapters and {len(unique_recent_files)} recently updated files.")
    print(f"Added a gallery with {len(image_links_with_context)} random images.")
    print(f"Set title to 'Cordisalia' in the frontmatter.")

if __name__ == "__main__":
    update_index_file()