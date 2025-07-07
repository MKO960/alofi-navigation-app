#!/usr/bin/env python3
"""
Script to split large files into smaller chunks for GitHub upload.
Splits vienna_networks.pkl into chunks smaller than 25MB.
"""

import os
import math

def split_file(input_file, output_dir, chunk_size_mb=24):
    """
    Split a large file into smaller chunks.
    
    Args:
        input_file (str): Path to the input file
        output_dir (str): Directory to save the chunks
        chunk_size_mb (int): Maximum size of each chunk in MB
    """
    chunk_size_bytes = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
    
    # Get file size
    file_size = os.path.getsize(input_file)
    print(f"Original file size: {file_size / (1024*1024):.2f} MB")
    
    # Calculate number of chunks needed
    num_chunks = math.ceil(file_size / chunk_size_bytes)
    print(f"Will create {num_chunks} chunks of max {chunk_size_mb}MB each")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    chunk_files = []
    
    with open(input_file, 'rb') as infile:
        for chunk_num in range(num_chunks):
            chunk_filename = f"{base_name}_part_{chunk_num + 1:02d}.chunk"
            chunk_path = os.path.join(output_dir, chunk_filename)
            chunk_files.append(chunk_filename)
            
            print(f"Creating chunk {chunk_num + 1}/{num_chunks}: {chunk_filename}")
            
            with open(chunk_path, 'wb') as outfile:
                bytes_written = 0
                while bytes_written < chunk_size_bytes:
                    # Read in smaller blocks to avoid memory issues
                    block_size = min(8192, chunk_size_bytes - bytes_written)
                    block = infile.read(block_size)
                    
                    if not block:  # End of file
                        break
                        
                    outfile.write(block)
                    bytes_written += len(block)
            
            chunk_size_actual = os.path.getsize(chunk_path)
            print(f"  Chunk size: {chunk_size_actual / (1024*1024):.2f} MB")
    
    # Create a manifest file with chunk information
    manifest_path = os.path.join(output_dir, f"{base_name}_manifest.txt")
    with open(manifest_path, 'w') as manifest:
        manifest.write(f"Original file: {os.path.basename(input_file)}\n")
        manifest.write(f"Original size: {file_size} bytes\n")
        manifest.write(f"Number of chunks: {num_chunks}\n")
        manifest.write(f"Chunk files:\n")
        for i, chunk_file in enumerate(chunk_files, 1):
            chunk_path = os.path.join(output_dir, chunk_file)
            chunk_size = os.path.getsize(chunk_path)
            manifest.write(f"  {i:02d}. {chunk_file} ({chunk_size} bytes)\n")
    
    print(f"\nSplitting complete!")
    print(f"Created {num_chunks} chunks in: {output_dir}")
    print(f"Manifest file: {manifest_path}")
    
    return chunk_files, manifest_path

if __name__ == "__main__":
    input_file = "/home/ubuntu/upload/vienna_networks.pkl"
    output_dir = "/home/ubuntu/vienna_split"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        exit(1)
    
    chunk_files, manifest = split_file(input_file, output_dir)
    
    print(f"\nFiles created:")
    for chunk in chunk_files:
        print(f"  - {chunk}")
    print(f"  - {os.path.basename(manifest)}")

