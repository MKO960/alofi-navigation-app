#!/usr/bin/env python3
"""
Script to reconstruct the original file from split chunks.
Reassembles vienna_networks.pkl from its chunks.
"""

import os
import hashlib

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def reconstruct_file(chunk_dir, output_file=None):
    """
    Reconstruct the original file from chunks.
    
    Args:
        chunk_dir (str): Directory containing the chunk files
        output_file (str): Path for the reconstructed file (optional)
    """
    # Read manifest file to get chunk information
    manifest_files = [f for f in os.listdir(chunk_dir) if f.endswith('_manifest.txt')]
    
    if not manifest_files:
        print("Error: No manifest file found!")
        return False
    
    manifest_path = os.path.join(chunk_dir, manifest_files[0])
    
    # Parse manifest
    chunk_files = []
    original_filename = None
    original_size = None
    
    with open(manifest_path, 'r') as manifest:
        lines = manifest.readlines()
        for line in lines:
            if line.startswith("Original file:"):
                original_filename = line.split(": ", 1)[1].strip()
            elif line.startswith("Original size:"):
                original_size = int(line.split(": ", 1)[1].split()[0])
            elif line.startswith("  ") and ".chunk" in line:
                # Extract chunk filename from manifest line
                # Format: "  01. vienna_networks_part_01.chunk (25165824 bytes)"
                parts = line.strip().split(". ", 1)
                if len(parts) > 1:
                    chunk_filename = parts[1].split(" (")[0]
                    chunk_files.append(chunk_filename)
    
    if not chunk_files:
        print("Error: No chunk files found in manifest!")
        return False
    
    # Set output filename if not provided
    if output_file is None:
        output_file = os.path.join(chunk_dir, f"reconstructed_{original_filename}")
    
    print(f"Reconstructing: {original_filename}")
    print(f"Expected size: {original_size / (1024*1024):.2f} MB")
    print(f"Number of chunks: {len(chunk_files)}")
    print(f"Output file: {output_file}")
    
    # Reconstruct the file
    total_bytes_written = 0
    
    with open(output_file, 'wb') as outfile:
        for i, chunk_filename in enumerate(chunk_files, 1):
            chunk_path = os.path.join(chunk_dir, chunk_filename)
            
            if not os.path.exists(chunk_path):
                print(f"Error: Chunk file not found: {chunk_path}")
                return False
            
            chunk_size = os.path.getsize(chunk_path)
            print(f"Processing chunk {i}/{len(chunk_files)}: {chunk_filename} ({chunk_size / (1024*1024):.2f} MB)")
            
            with open(chunk_path, 'rb') as chunk_file:
                while True:
                    block = chunk_file.read(8192)
                    if not block:
                        break
                    outfile.write(block)
                    total_bytes_written += len(block)
    
    # Verify reconstruction
    reconstructed_size = os.path.getsize(output_file)
    print(f"\nReconstruction complete!")
    print(f"Reconstructed file size: {reconstructed_size / (1024*1024):.2f} MB")
    
    if original_size and reconstructed_size == original_size:
        print("✅ Size verification: PASSED")
        success = True
    else:
        print("❌ Size verification: FAILED")
        print(f"Expected: {original_size} bytes, Got: {reconstructed_size} bytes")
        success = False
    
    return success

def verify_chunks_exist(chunk_dir):
    """Verify all required chunk files exist."""
    manifest_files = [f for f in os.listdir(chunk_dir) if f.endswith('_manifest.txt')]
    
    if not manifest_files:
        return False, "No manifest file found"
    
    manifest_path = os.path.join(chunk_dir, manifest_files[0])
    chunk_files = []
    
    with open(manifest_path, 'r') as manifest:
        lines = manifest.readlines()
        for line in lines:
            if line.startswith("  ") and ".chunk" in line:
                # Format: "  01. vienna_networks_part_01.chunk (25165824 bytes)"
                parts = line.strip().split(". ", 1)
                if len(parts) > 1:
                    chunk_filename = parts[1].split(" (")[0]
                    chunk_files.append(chunk_filename)
    
    missing_files = []
    for chunk_file in chunk_files:
        chunk_path = os.path.join(chunk_dir, chunk_file)
        if not os.path.exists(chunk_path):
            missing_files.append(chunk_file)
    
    if missing_files:
        return False, f"Missing chunk files: {', '.join(missing_files)}"
    
    return True, f"All {len(chunk_files)} chunk files found"

if __name__ == "__main__":
    chunk_dir = "/home/ubuntu/vienna_split"
    
    # Verify chunks exist
    chunks_ok, message = verify_chunks_exist(chunk_dir)
    print(f"Chunk verification: {message}")
    
    if not chunks_ok:
        print("Cannot proceed with reconstruction.")
        exit(1)
    
    # Reconstruct the file
    success = reconstruct_file(chunk_dir)
    
    if success:
        print("\n🎉 File reconstruction completed successfully!")
        print("\nTo use the reconstructed file:")
        print("1. Copy 'reconstructed_vienna_networks.pkl' to your project directory")
        print("2. Rename it to 'vienna_networks.pkl'")
        print("3. Use it in your application as normal")
    else:
        print("\n❌ File reconstruction failed!")
        exit(1)

