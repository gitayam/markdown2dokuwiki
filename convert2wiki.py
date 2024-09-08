import os
import shutil
import re
import sys
from pathlib import Path
# Definitions
internal_wiki_url = "https://wiki.irregularchat.com/"


# Function to print help message
def print_help():
    print("Usage: python wiki-conversion.py")
    print("This script converts Markdown files to DokuWiki or MediaWiki format.")
    print("It performs the following steps:")
    print("1. Cleans the Markdown files by removing YAML front matter, HTML comments, and other problematic sections.")
    print("2. Moves media files like images, PDFs, and others to the media/ directory.")
    print("3. Flattens the directory structure with an option to protect certain subdirectories.")
    print("4. Converts the Markdown files to DokuWiki or MediaWiki format.")
    print("5. Provides instructions to copy the converted files to the wiki container.")
    print("The script requires the following user inputs:")
    print("1. Conversion type: DokuWiki or MediaWiki.")
    print("2. Directory flattening option.")
    print("3. Protected directories for flattening.")
    print("The script can be run without any arguments.")
    print("Example: python wiki-conversion.py")
    sys.exit(0)

# Function to print progress messages
def print_progress(message):
    print(f"\033[1;32m{message}\033[0m")

# Function to print error messages
def print_error(message):
    print(f"\033[1;31m{message}\033[0m", file=sys.stderr)

# General function to read and write files safely
def read_file(file):
    with open(file, 'r', newline='') as f:
        return f.read()

def write_file(file, content):
    with open(file, 'w', newline='') as f:
        f.write(content)

# Function to clean the Markdown file before converting
def clean_markdown_file(file):
    content = read_file(file)
    original_content = content  # Keep a copy of the original content for comparison

    # Step 1: Remove YAML front matter if present (block between two "---" lines)
    content = re.sub(r'^---[\s\S]+?---\s*', '', content)
    # Step 2: Remove any remaining "---" markers in the content
    content = content.replace('---', '')
    # Step 3: Remove any HTML comments
    content = re.sub(r'<!--(.*?)-->', '', content, flags=re.DOTALL)
    # Step 4: Remove any problematic sections like raw HTML or LaTeX
    content = re.sub(r'```(html|latex)[\s\S]+?```', '', content, flags=re.IGNORECASE)
    # Step 5: Remove any raw HTML tags
    content = re.sub(r'<(.*?)>', '', content)
    # Step 6: Replace internal wiki links which are in the format [Title](internal_wiki_url/content/here) with [Title](/content/here)
    # This is to ensure that the links work correctly after conversion
    content = re.sub(r'\[([^\]]+)\]\(' + internal_wiki_url + r'([^\)]+)\)', r'[\1](/\2)', content)
    # Step 7: Remove path for links to leave only the file name
    content = re.sub(r'\[([^\]]+)\]\(([^\/]+\/)*([^\)]+)\)', r'[\1](\3)', content)
    # Step 8: Remove .md or .html extensions from links
    content = re.sub(r'\[([^\]]+)\]\(([^\.]+)\.md\)', r'[\1](\2)', content)
    content = re.sub(r'\[([^\]]+)\]\(([^\.]+)\.html\)', r'[\1](\2)', content)
    # Log any removed content
    if content != original_content:
        print_progress(f"Cleaned content in {file}. Removed YAML front matter or problematic sections.")
        log_removed_content(file, original_content, content)

    # Save the cleaned content back to the file
    write_file(file, content)

def log_removed_content(file, original_content, cleaned_content):
    log_file = file + ".log"
    with open(log_file, 'w') as f:
        f.write("Original Content:\n")
        f.write(original_content)
        f.write("\n\nCleaned Content:\n")
        f.write(cleaned_content)
    print_progress(f"Logged removed content to {log_file}")

# Function to move media files like images, PDFs, and others to the media/ directory
def move_media_files(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp4', '.docx')):
                shutil.move(os.path.join(root, file), os.path.join(dest_dir, file))

# Function to flatten directories with optional protection for certain subdirectories
def flatten_directory(src_dir, dest_dir, protected_dirs):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_dir = os.path.relpath(root, src_dir)

            # Check if the current directory is a protected one
            for protected_dir in protected_dirs:
                if relative_dir.startswith(protected_dir):
                    # Maintain the directory structure for protected dirs
                    dest_subdir = os.path.join(dest_dir, protected_dir)
                    os.makedirs(dest_subdir, exist_ok=True)
                    shutil.copy(file_path, os.path.join(dest_subdir, file))
                    break
            else:
                # Flatten non-protected files
                shutil.copy(file_path, os.path.join(dest_dir, file))

# Function to convert Markdown to DokuWiki format (simulate conversion)
def convert_markdown_to_dokuwiki(file):
    print_progress(f"Converting {file} to DokuWiki format.")
    # Placeholder conversion logic
    content = read_file(file).replace("#", "======")  # Simulate Markdown to DokuWiki conversion
    write_file(file.replace('.md', '.txt'), content)

# Function to convert Markdown to MediaWiki format (simulate conversion)
def convert_markdown_to_mediawiki(file):
    print_progress(f"Converting {file} to MediaWiki format.")
    # Placeholder conversion logic
    content = read_file(file).replace("#", "=")  # Simulate Markdown to MediaWiki conversion
    write_file(file.replace('.md', '.txt'), content)

# Function to convert all Markdown files
def process_markdown_files(conversion_type):
    """Processes all Markdown files in the current directory."""
    for md_file in Path(".").rglob("*.md"):
        print(f"Processing {md_file}")
        clean_markdown_file(md_file)
        if conversion_type == "dokuwiki":
            convert_markdown_to_dokuwiki(md_file)
        elif conversion_type == "mediawiki":
            convert_markdown_to_mediawiki(md_file)
def search_wiki_container():
    # docker ps and search for wiki container dokuwiki or wikimedia. Save container name to variables
    wiki_container = os.popen('docker ps | grep dokuwiki').read().split()[0]
    wiki_container = os.popen('docker ps | grep wikimedia').read().split()[0]
    return wiki_container
def print_instructions(wiki_container):
    if wiki_container == "":
        print_error("Could not find the wiki container. Please copy the files manually.")
        return
    elif wiki_container == "dokuwiki":
        wiki_container_path = "/app/www/html/data/pages/wiki/"
    elif wiki_container == "wikimedia":
        wiki_container_path = "/var/www/html/Import"
    print(f"Copy the contents of the converted directory to the wiki container {wiki_container} using the following command:")
    print(f"docker cp converted_directory/. {wiki_container}:/app/www/public/data/pages/wiki/")
    print("After copying the files, access the wiki in your browser to verify the changes.")
    print("Remember to restart the wiki container if necessary.")
# Main function
def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print_error("Usage: python script.py <source_directory>")
        sys.exit(1)

    src_dir = Path(sys.argv[1])

    # Validate if the given path is a directory
    if not src_dir.is_dir():
        print_error(f"The path {src_dir} is not a valid directory.")
        sys.exit(1)

    # Create a new directory in the current working directory to store processed files
    output_dir = Path.cwd() / f"{src_dir.name}_converted"
    output_dir.mkdir(exist_ok=True)

    # Ask the user for conversion type: DokuWiki or MediaWiki
    conversion_choice = input("Choose the conversion type:\n1. DokuWiki\n2. MediaWiki\nEnter your choice (1/2): ")

    if conversion_choice == '1':
        conversion_type = "dokuwiki"
    elif conversion_choice == '2':
        conversion_type = "mediawiki"
    else:
        print_error("Invalid choice. Exiting.")
        sys.exit(1)

    # Ask for directory flattening option
    flatten_choice = input("Do you want to flatten the directory structure? (y/n): ").strip().lower()

    if flatten_choice == 'y':
        protected_input = input("Enter comma-separated directory names you want to protect from flattening: ")
        protected_dirs = [d.strip() for d in protected_input.split(",")] if protected_input else []

        print_progress("Flattening the directory structure and protecting specified directories.")
        flat_dir = output_dir / "flattened_directory"
        os.makedirs(flat_dir, exist_ok=True)

        # Flatten directories into the new directory, while protecting specific directories
        flatten_directory(src_dir, flat_dir, protected_dirs)
        process_dir = flat_dir  # Use the flattened directory for further processing
    else:
        # Copy files to the output directory without flattening
        print_progress("Copying files to output directory without flattening.")
        shutil.copytree(src_dir, output_dir, dirs_exist_ok=True)
        process_dir = output_dir  # Use the copied directory for processing

    # Move media files to the 'media' directory inside the output directory
    media_dir = process_dir / "media"
    move_media_files(process_dir, media_dir)

    # Process and convert Markdown files
    process_markdown_files(process_dir, conversion_type)

    print_progress("Conversion completed successfully.")
    print_instructions(search_wiki_container())

if __name__ == '__main__':
    main()