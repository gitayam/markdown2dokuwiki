#!/bin/bash

# Configuration
CONTAINER_NAME="dokuwiki"
CONTAINER_DEST_DIR="/app/www/public/data/pages"
USER_ID="abc"
GROUP_ID="abc"

# Function to print progress messages
print_progress() {
  echo -e "\033[1;32m$1\033[0m"
}

# Check OS type
os_type=$(uname)
if [[ "$os_type" != "Linux" && "$os_type" != "Darwin" ]]; then
  echo "This script only supports macOS and Linux."
  exit 1
fi

print_progress "Operating System: $os_type"

# Function to check and install required packages
check_and_install_package() {
  package=$1
  install_command=$2
  if ! command -v $package &> /dev/null; then
    print_progress "$package not found. Installing..."
    eval $install_command
    if ! command -v $package &> /dev/null; then
      echo "Failed to install $package. Please install it manually."
      exit 1
    fi
  fi
}

# Check for required packages
if [[ "$os_type" == "Linux" ]]; then
  check_and_install_package "pandoc" "sudo apt-get install -y pandoc"
  check_and_install_package "awk" "sudo apt-get install -y gawk"
  check_and_install_package "sed" "sudo apt-get install -y sed"
elif [[ "$os_type" == "Darwin" ]]; then
  check_and_install_package "pandoc" "brew install pandoc"
  check_and_install_package "awk" "brew install gawk"
  check_and_install_package "sed" "brew install gnu-sed --with-default-names"
fi

print_progress "All required packages are installed."

# Get the name of the current working directory
current_dir=$(basename "$PWD")
new_dir="${current_dir}-dokuwiki"

# Create the new directory
print_progress "Creating new directory: ../$new_dir"
mkdir -p "../$new_dir"

# Copy all contents to the new directory (excluding the new directory itself)
print_progress "Copying contents to the new directory..."
rsync -av --exclude="${new_dir}" ./ "../$new_dir"

# Change to the new directory
cd "../$new_dir" || { echo "Failed to change to new directory"; exit 1; }

# Function to handle Markdown tables
convert_md_tables_to_dw() {
  awk '
  BEGIN {
    FS="|";
    OFS="|";
  }
  {
    if (NF > 1) {
      $1 = " ^" $1;
      for (i = 2; i <= NF; i++) {
        $i = " " $i " ";
      }
      $NF = $NF " ^";
    }
    print $0;
  }' "$1"
}

# Run the conversion script
print_progress "Processing Markdown files..."
find . -iname "*.md" -exec sh -c '
  for f do
    echo "Processing $f"
    convert_md_tables_to_dw "$f" > "${f%.md}_converted.md"
    mv "${f%.md}_converted.md" "$f"
    pandoc --wrap=preserve -f markdown -t dokuwiki "$f" -o "${f%.md}.txt" || { echo "Failed to convert $f with pandoc"; exit 1; }
  done
' sh {} +

# Post-process the converted files to add backslashes for line breaks
print_progress "Post-processing converted files..."
find . -iname "*.txt" -exec sh -c '
    for f do
        echo "Post-processing $f"
        sed -i -e "s/\([^=^ ^>]\)$/\1\\\\/g" -e "s/%%//g" -e "s/^$/\\\\/g" "$f" || { echo "Failed to process $f with sed"; exit 1; }
    done
' sh {} +

# Handle YAML front matter issue
print_progress "Handling YAML front matter..."
find . -iname "*.md" -exec sh -c '
    for f do
        echo "Handling YAML front matter in $f"
        # Remove YAML front matter if present
        sed -i -e "/^---$/,/^---$/d" "$f" || { echo "Failed to remove YAML front matter from $f"; exit 1; }
    done
' sh {} +

# Convert markdown to dokuwiki format again for the files with YAML front matter
print_progress "Reprocessing Markdown files..."
find . -iname "*.md" -exec sh -c '
    for f do
        echo "Reprocessing $f"
        pandoc --wrap=preserve -f markdown -t dokuwiki "$f" -o "${f%.md}.txt" || { echo "Failed to convert $f with pandoc"; exit 1; }
    done
' sh {} +

# Remove the original markdown files
print_progress "Removing original Markdown files..."
find . -iname "*.md" -exec rm -f {} +

# Ensure the target directory in the container exists
print_progress "Ensuring target directory exists in the Docker container..."
docker exec -it "$CONTAINER_NAME" mkdir -p "$CONTAINER_DEST_DIR"

# Copy the converted files to the Docker container
print_progress "Copying converted files to the Docker container..."
docker cp "./." "$CONTAINER_NAME:$CONTAINER_DEST_DIR/"

# Set the correct permissions inside the container
print_progress "Setting permissions in the Docker container..."
docker exec -it "$CONTAINER_NAME" chown -R "$USER_ID:$GROUP_ID" "$CONTAINER_DEST_DIR"
docker exec -it "$CONTAINER_NAME" chmod -R 755 "$CONTAINER_DEST_DIR"

# Change back to the original directory
print_progress "Changing back to the original directory..."
cd "$SOURCE_DIR" || { echo "Failed to change back to original directory"; exit 1; }

print_progress "Conversion and copy complete."
