import streamlit as st
import os
import subprocess
import shutil
import requests

# Function to process APK file
def process_apk(input_path, output_dir):
    # Run apk-mitm command
    command = f"java -jar uber-apk-signer.jar --apks {input_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    st.write(f"Processed APK file found at: {result}")
    # Check if the process was successful
    if result.returncode == 0:
        out_path = input_path.replace('.apk', '-aligned-signed.apk')
        return out_path
    else:
        st.error(f"Error processing APK: {result.stderr}")
        return None

# Streamlit app interface
st.title("APK File Processor")

# File upload
uploaded_file = st.file_uploader("Upload APK file", type=['apk', 'xapk', 'apks'])

# URL upload
url_input = st.text_input("Or enter APK URL")

if uploaded_file is not None or url_input:
    # Create directories if they don't exist
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    if uploaded_file is not None:
        # Save uploaded file
        input_path = os.path.join(upload_dir, uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())
    elif url_input:
        # Download APK from URL
        st.write("Downloading APK from URL...")
        response = requests.get(url_input)
        if response.status_code == 200:
            input_path = os.path.join(upload_dir, os.path.basename(url_input))
            with open(input_path, "wb") as f:
                f.write(response.content)
        else:
            st.error("Failed to download APK from URL. Please check the URL and try again.")
            st.stop()

    # Define output directory for the patched APK
    output_dir = upload_dir

    # Process APK
    st.write("Processing APK...")
    result = process_apk(input_path, output_dir)
    
    if result:
        st.success("APK processed successfully!")
        st.write("Processing result:")
        st.text(result)
        
        # Extract the patched APK file name from the output path
        output_file_name = os.path.basename(result)
        output_path = os.path.join(output_dir, output_file_name)
        
        # Check if the processed APK file exists
        if os.path.exists(output_path):
            st.write(f"Processed APK file found at: {output_path}")
            
            # Provide download link for the patched APK file
            with open(output_path, "rb") as f:
                file_data = f.read()
                if file_data:
                    st.download_button(
                        label="Download Patched APK",
                        data=file_data,
                        file_name=output_file_name,
                        mime="application/vnd.android.package-archive"
                    )
                else:
                    st.error("Failed to read file data.")
        else:
            st.error("Processed APK file not found. Please try again.")
    else:
        st.error("Failed to process APK. Please try again.")
    
    # Clean up the uploaded and processed files
    def cleanup_files(input_path, output_path):
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

    # Cleanup is done after download button appears to ensure the file is available for download
    cleanup_files(input_path, output_path)
