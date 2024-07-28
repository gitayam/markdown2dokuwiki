# markdown2dokuwiki - Convert and Transfer Markdown Files to DokuWiki

## Overview

`md2doku.sh` is a shell script designed to convert Markdown files to DokuWiki format and transfer them to a specified directory within a Docker container running DokuWiki. The script supports both Linux and macOS operating systems, ensures that all required packages are installed, and provides user-friendly progress messages throughout the process.

This script is built upon the groundwork laid by [obsidian2dokuwiki](https://github.com/vzeller/obsidian2dokuwiki).

## Features

- **OS Compatibility**: Supports Linux and macOS.
- **Package Verification**: Checks for and installs required packages (`pandoc`, `awk`, `sed`).
- **Markdown to DokuWiki Conversion**: Converts Markdown files to DokuWiki format using `pandoc`.
- **YAML Front Matter Handling**: Removes YAML front matter if present in Markdown files.
- **File Transfer**: Copies the converted files to a specified directory within a Docker container.
- **Permission Setting**: Sets the appropriate permissions for the transferred files inside the Docker container.
- **User-Friendly Output**: Provides clear and informative progress messages.

## Requirements

- **Operating Systems**: Linux, macOS
- **Packages**:
  - `pandoc`
  - `awk`
  - `sed`
- **Docker**: Installed and running
- **DokuWiki Docker Container**: [linuxserver/dokuwiki](https://hub.docker.com/r/linuxserver/dokuwiki)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/gitayam/markdown2dokuwiki.git
   cd markdown2dokuwiki
   PWD=$(pwd)
   ```

2. **Make the Script Executable**:
   ```bash
   chmod +x $PWD'/md2doku.sh"
   ```

3. **Create an Alias or Move the Script**:
   To run the script from any directory, you can create an alias OR move the script to a directory in your PATH. You DON'T need to do both.

   This will leave the script in the cloned repository directory but allow you to run it from any location using the alias of the absolute path.
   **Create an Alias**:
   ```bash
   echo 'alias md2doku="'$PWD'/md2doku.sh"' >> ~/.bashrc
   source ~/.bashrc
   ```

   Use this option if you want to run the script from any directory without moving it.
   **Move the Script**:
   ```bash
   sudo mv $PWD/md2doku.sh /usr/local/bin/md2doku
   ```

## Usage

**Run the Script**:

This script should be run inside the top-level Markdown directory (e.g., the Obsidian vault).

1. **Navigate to Your Markdown Directory**:
   ```bash
   cd path/to/your/markdown/directory
   ```

2. **Run the Script**:
   ```bash
   md2doku
   ```

## Configuration

The script includes a few configurable variables that you may need to adjust based on your setup:

- `CONTAINER_NAME`: Name of the Docker container running DokuWiki.
- `CONTAINER_DEST_DIR`: Destination directory within the Docker container where the converted files will be copied.
- `USER_ID`: User ID for setting file ownership inside the Docker container.
- `GROUP_ID`: Group ID for setting file ownership inside the Docker container.

## References

- [DokuWiki](https://www.dokuwiki.org/dokuwiki)
- [obsidian2dokuwiki](https://github.com/vzeller/obsidian2dokuwiki)
- [DokuWiki Docker Container](https://hub.docker.com/r/linuxserver/dokuwiki)

## Script Execution Flow

1. **Check OS Compatibility**: Verifies if the script is being run on a supported OS (Linux or macOS).
2. **Verify and Install Packages**: Ensures that `pandoc`, `awk`, and `sed` are installed. If not, it installs them.
3. **Create and Copy Files**: Creates a new directory for converted files and copies the original files to this directory.
4. **Convert Markdown to DokuWiki**: Converts Markdown files to DokuWiki format using `pandoc`.
5. **Handle YAML Front Matter**: Removes YAML front matter from Markdown files if present.
6. **Post-Processing**: Adds backslashes for line breaks in the converted files.
7. **Transfer Files to Docker Container**: Copies the converted files to the specified directory within the Docker container and sets the appropriate permissions.

## Troubleshooting

- **Permission Issues**: Ensure you have the necessary permissions to create directories and install packages.
- **Package Installation**: If the script fails to install a package, manually install it and rerun the script.
- **Docker Access**: Ensure Docker is running and you have access to the specified container.
