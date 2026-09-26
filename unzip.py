import zipfile
import os
import shutil

def recursive_extract(zip_path, extract_to="."):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            print(f"Extracted: {zip_path}")
            
            # Find all newly created zip files and extract them too
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    if file.endswith('.zip'):
                        next_zip = os.path.join(root, file)
                        # CAUTION: This is where the explosion happens
                        recursive_extract(next_zip, extract_to)
    except Exception as e:
        print(f"Error or Crash at {zip_path}: {e}")

# WARNING: Running this on a 10PB bomb will likely destroy your VM's filesystem.
recursive_extract("zipbomb_10pb.zip")