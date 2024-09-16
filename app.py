import streamlit as st
import os
import subprocess
import tempfile
import shutil
import zipfile

# Function to process APK file
def process_apk(file_path, output_path):
    # Run apk-mitm command
    command = f"apk-mitm {file_path} -o {output_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

# Function to zip the processed APK file
def zip_file(file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))

# Streamlit app interface
st.title("APK File Processor")

# File upload
uploaded_file = st.file_uploader("Upload APK file", type="apk")
if uploaded_file is not None:
    # Create temporary file paths
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, uploaded_file.name)
    output_path = os.path.join(temp_dir, "patched-" + uploaded_file.name)
    zip_path = os.path.join(temp_dir, "patched-apk.zip")

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
    
    # Process APK
    st.write("Processing APK...")
    result = process_apk(input_path, output_path)
    
    if result.returncode == 0:
        st.success("APK processed successfully!")
        st.write("Processing result:")
        st.text(result.stdout)
        
        # Zip the processed APK file
        if os.path.exists(output_path):
            zip_file(output_path, zip_path)
            
            # Provide download link for the zip file
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Download Patched APK (ZIP)",
                    data=f,
                    file_name=os.path.basename(zip_path),
                    mime="application/zip"
                )
        else:
            st.error("Processed APK file not found. Please try again.")
    else:
        st.error(f"Error processing APK: {result.stderr}")
