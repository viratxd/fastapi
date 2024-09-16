import streamlit as st
import os
import subprocess
import tempfile
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

    st.write(f"Uploaded APK saved to: {input_path}")

    # Process APK
    st.write("Processing APK...")
    result = process_apk(input_path, output_path)
    
    st.write(f"Process command: apk-mitm {input_path} -o {output_path}")
    st.write(f"Processing output: {result.stdout}")
    st.write(f"Processing error: {result.stderr}")

    if result.returncode == 0:
        st.success("APK processed successfully!")
        
        # Debugging: Check if the processed APK file exists
        if os.path.exists(output_path):
            st.write(f"Processed APK file created at: {output_path}")

            # Zip the processed APK file
            zip_file(output_path, zip_path)
            st.write(f"ZIP file created at: {zip_path}")
            
            # Check if ZIP file exists before providing download link
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="Download Patched APK (ZIP)",
                        data=f,
                        file_name=os.path.basename(zip_path),
                        mime="application/zip"
                    )
            else:
                st.error(f"ZIP file not created at: {zip_path}")
        else:
            st.error(f"Processed APK file not found at: {output_path}")
    else:
        st.error(f"Error processing APK: {result.stderr}")
