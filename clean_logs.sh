#!/bin/bash

# Specify the path to your log folder
log_folder="logs"

# Check if the log folder exists
if [ -d "$log_folder" ]; then
    # Change to the log folder
    cd "$log_folder" || exit

    # Remove all files with a .log extension
    find . -type f -name "*.log" -exec rm -f {} +

    echo "Log files cleaned successfully."
else
    echo "Log folder not found: $log_folder"
fi