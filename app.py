import streamlit as st
import os
import subprocess
import tempfile
import shutil

# Function to process APK file
def process_apk(file_path, output_path):
    # Run apk-mitm command
    command = f"apk-mitm {file_path} -o {output_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

# Streamlit app interface
st.title("APK File Processor")

# File upload
uploaded_file = st.file_uploader("Upload APK file", type="apk")
if uploaded_file is not None:
    # Create temporary file paths
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, uploaded_file.name)
    output_path = os.path.join(temp_dir, "patched-" + uploaded_file.name)

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
        
        # Check if the patched APK file exists before providing download link
        if os.path.exists(output_path):
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Patched APK",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="application/vnd.android.package-archive"
                )
        else:
            st.error("Processed APK file not found. Please try again.")
    else:
        st.error(f"Error processing APK: {result.stderr}")
