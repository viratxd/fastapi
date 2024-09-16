import streamlit as st
import os
import subprocess
import shutil
import tempfile

# Function to install Node.js and apk-mitm
def install_node_and_apk_mitm():
    # Install Node.js
    st.write("Installing Node.js...")
    os.system("curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
    os.system("sudo apt-get install -y nodejs")
    
    # Install apk-mitm
    st.write("Installing apk-mitm...")
    os.system("sudo npm install -g apk-mitm")

# Function to process APK file
def process_apk(file_path, output_path):
    # Run apk-mitm command
    command = f"apk-mitm {file_path} -o {output_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

# Streamlit app interface
st.title("APK File Processor")

# Install Node.js and apk-mitm if not installed
if not shutil.which("apk-mitm"):
    install_node_and_apk_mitm()

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
        
        # Provide download link for processed APK
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Patched APK",
                data=f,
                file_name=os.path.basename(output_path),
                mime="application/vnd.android.package-archive"
            )
    else:
        st.error(f"Error processing APK: {result.stderr}")
