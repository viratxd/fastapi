import streamlit as st
import os
import subprocess
import shutil
import zipfile
import requests

# Function to debug APK file
def debug_apk(input_path, output_dir): 
    # Run apk-mitm command
    command = f"apk-mitm {input_path} -o {output_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        # Extract the patched file name from stdout
        output_file_name = result.stdout.split("Patched file: ")[-1].strip()
        output_path = os.path.join(output_dir, output_file_name)
        return output_path
    else:
        st.error(f"Error debugging APK: {result.stderr}")
        return None

# Function to process XAPK file
def process_xapk(xapk_path):
    """
    Process XAPK file: rename to ZIP, extract contents, merge with APKEditor.jar, and sign the APK.
    
    Args:
        xapk_path (str): Path to the XAPK file
        
    Returns:
        str: Path to the signed APK if successful, None if failed
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
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Remove the ZIP file after extraction
        os.remove(zip_path)
        
        # Run APKEditor.jar command to merge the extracted files
        command = f'java -jar APKEditor.jar m -i "{extract_dir}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Define the path for the merged APK
            merged_apk_path = os.path.join(folder, f"{name_without_ext}_merged.apk")
            st.write(f"Merged APK created at: {merged_apk_path}")
            
            # Proceed to sign the merged APK
            signed_apk_path = process_sign(merged_apk_path)
            return signed_apk_path
        else:
            st.error(f"Error merging APK: {result.stderr}")
            return None
            
    except Exception as e:
        st.error(f"Error processing XAPK: {str(e)}")
        # Clean up in case of error
        shutil.rmtree(extract_dir, ignore_errors=True)
        return None

# Function to sign APK file
def process_sign(apk_path):
    """
    Sign the APK file using uber-apk-signer.
    
    Args:
        apk_path (str): Path to the APK file to be signed.
        
    Returns:
        str: Path to the signed APK if successful, None if failed.
    """
    folder = os.path.dirname(apk_path)
    command = f"java -jar uber-apk-signer.jar --apks {apk_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        # Extract the path of the signed APK from the output directory
        signed_apk_path = apk_path.replace('.apk', '-aligned-debugSigned.apk')

        # Check if the signed APK exists at the expected path
        if os.path.exists(signed_apk_path):
            st.write("APK signing successful!")
            return signed_apk_path
        else:
            st.error("APK signing completed, but the signed file could not be found.")
            return None
    else:
        # Display the error message in a more user-friendly way
        st.error(f"Error signing APK: {result.stderr}")
        return None

# Streamlit app interface
st.title("APK File Processor")

# File upload
uploaded_file = st.file_uploader("Upload APK file", type=['apk', 'xapk', 'apks'])

# URL upload
url_input = st.text_input("Or enter APK URL")

# Radio buttons to select the processing type
processing_option = st.radio("Choose the processing type:", ('Process XAPK', 'Sign APK', 'Debug APK'))

if uploaded_file is not None or url_input:
    # Create directories if they don't exist
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    if uploaded_file is not None:
        # Save uploaded file
        input_path = os.path.join(upload_dir, uploaded_file.name)
        
        # Write the uploaded file to the filesystem
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        # Now that the file is saved, rename it if it contains spaces
        if " " in uploaded_file.name:
            new_name = uploaded_file.name.replace(" ", "_")  # Replace spaces with underscores
            new_input_path = os.path.join(upload_dir, new_name)

            # Only rename if the new name is different
            if new_input_path != input_path:
                os.rename(input_path, new_input_path)
                input_path = new_input_path  # Update input_path to new name

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

    # Define output directory for the processed APK
    output_dir = upload_dir

    # Execute the process based on user choice
    if processing_option == 'Process XAPK' and input_path.endswith('.xapk'):
        st.write("Processing XAPK...")
        output_path = process_xapk(input_path)
    elif processing_option == 'Sign APK' and input_path.endswith('.apk'):
        st.write("Signing APK...")
        output_path = process_sign(input_path)
    elif processing_option == 'Debug APK' and input_path.endswith('.apk'):
        st.write("Debugging APK...")
        output_path = debug_apk(input_path, output_dir)
    else:
        st.error("The selected process is not compatible with the uploaded file type. Please ensure the file type matches your selection.")
        output_path = None

    # Handle the result of processing
    if output_path:
        st.success("APK processed successfully!")
        st.write("Output path:")
        st.text(output_path)

        # Provide download link for the processed APK file
        if os.path.exists(output_path):
            with open(output_path, "rb") as f:
                file_data = f.read()
                st.download_button(
                    label="Download Processed APK",
                    data=file_data,
                    file_name=os.path.basename(output_path),
                    mime="application/vnd.android.package-archive"
                )
        else:
            st.error("Processed APK file not found. Please try again.")
    else:
        st.error("Failed to process APK. Please try again.")

    # Clean up the uploaded and processed files
    def cleanup_files():
        shutil.rmtree(upload_dir, ignore_errors=True)

    # Cleanup is done after download button appears to ensure the file is available for download
    cleanup_files()
