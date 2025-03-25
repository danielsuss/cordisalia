#!/usr/bin/env python3
import os
import sys
import re
from collections import defaultdict
import frontmatter

def merge_markdown_files(input_directory, output_file):
    """
    Recursively merge all .md files from the specified directory and its subdirectories 
    into a single output file, grouped by directory.
    
    Args:
        input_directory (str): Path to the directory containing .md files
        output_file (str): Path to the output file where merged content will be saved
    """
    # Use a defaultdict to group files by their directory
    directory_files = defaultdict(list)
    
    # Get all .md files in the directory and its subdirectories
    for root, dirs, files in os.walk(input_directory):
        # Skip root directory and templates directory
        rel_root = os.path.relpath(root, input_directory)
        if rel_root in ['', '.', 'templates']:
            continue
        
        for file in files:
            if file.endswith('.md'):
                # Get full path and relative path from input directory
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, input_directory)
                
                # Get the directory path relative to input directory
                rel_dir = os.path.dirname(rel_path)
                
                # Store file information
                directory_files[rel_dir].append({
                    'filename': file,
                    'full_path': full_path
                })
    
    # Prepare the content
    merged_content = ""
    
    # Sort directories to ensure consistent output
    sorted_directories = sorted(directory_files.keys())
    
    # Iterate through directories
    for directory in sorted_directories:
        # Write directory header
        merged_content += f"## Directory: {directory}\n\n"
        
        # Sort files within each directory
        files_in_dir = sorted(directory_files[directory], key=lambda x: x['filename'])
        
        # Iterate through files in the directory
        for file_info in files_in_dir:
            # Write filename as a subheader
            merged_content += f"### {file_info['filename']}\n\n"
            
            # Read file content
            try:
                with open(file_info['full_path'], 'r', encoding='utf-8') as file:
                    merged_content += file.read() + "\n\n"
            except Exception as e:
                print(f"Error reading {file_info['filename']}: {e}")
    
    # Create a frontmatter post
    post = frontmatter.Post(merged_content, draft="true")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(frontmatter.dumps(post))
    
    # Count total files merged
    total_files = sum(len(files) for files in directory_files.values())
    print(f"Successfully merged {total_files} markdown files into {output_file}")

def main():
    # Check if correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python merge_markdown.py <input_directory> <output_file>")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    output_file = sys.argv[2]
    
    # Validate input directory
    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory")
        sys.exit(1)
    
    merge_markdown_files(input_directory, output_file)

if __name__ == "__main__":
    main()