import streamlit as st
import os
import subprocess
import shutil
import zipfile
import requests


def debug_apk(input_path, output_dir):
    """
    Run the apk-mitm command to debug the APK file.
    
    Args:
        input_path (str): Path to the APK file to be processed.
        output_dir (str): Directory where the output will be saved.
        
    Returns:
        str: Path to the output APK if successful, None if failed.
    """
    # Run apk-mitm command
    command = f"apk-mitm {input_path} -o {output_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        st.error(f"Error running apk-mitm: {result.stderr}")
        return None

    # Assuming the output APK file is in the output directory
    output_apk_path = os.path.join(output_dir, os.path.basename(input_path))  # Adjust this based on your output structure
    return output_apk_path


def process_xapk(xapk_path):
    """
    Process XAPK file: rename to ZIP, extract contents, run apk-mitm, and return the signed APK.
    
    Args:
        xapk_path (str): Path to the XAPK file.
        
    Returns:
        str: Path to the signed APK if successful, None if failed.
    """
    try:
        # Get the directory and filename without extension
        folder = os.path.dirname(xapk_path)
        name_without_ext = os.path.splitext(os.path.basename(xapk_path))[0]
        
        # Create paths for zip and extraction
        zip_path = os.path.join(folder, f"{name_without_ext}.zip")
        extract_dir = os.path.join(folder, name_without_ext)
        
        # Rename XAPK to ZIP and extract contents
        shutil.move(xapk_path, zip_path)

        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Call debug_apk (assuming you want to run it on an APK file located in the extracted directory)
        apk_file_path = os.path.join(extract_dir, 'your_apk_file.apk')  # Adjust based on your extracted files
        signed_apk_path = debug_apk(apk_file_path, extract_dir)

        # Ensure signed_apk_path is valid before opening
        if signed_apk_path:
            with open(signed_apk_path, "rb") as f:
                # Do something with the signed APK file
                # For example, you could read the contents or provide a download link
                st.download_button("Download Signed APK", data=f, file_name=os.path.basename(signed_apk_path))

        return signed_apk_path

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Streamlit UI
st.title("XAPK to APK Processor")
uploaded_file = st.file_uploader("Upload XAPK file", type=["xapk"])

if uploaded_file:
    # Save the uploaded file temporarily
    xapk_path = os.path.join("temp_dir", uploaded_file.name)
    os.makedirs("temp_dir", exist_ok=True)
    
    with open(xapk_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Process the uploaded XAPK file
    signed_apk = process_xapk(xapk_path)

    if signed_apk:
        st.success("APK processed successfully!")
    else:
        st.error("Failed to process the APK.")
