import bsdiff4
import base64
import json
import requests
import os
import tempfile
import shutil
import zipfile
import logging
from django.conf import settings
from django.core.files import File

logger = logging.getLogger(__name__)

def encrypt_data(client_id, scorm) -> str:
    """
    Encrypts the given client ID and SCORM data.

    Args:
        client_id (int): The client ID.
        scorm (str): The SCORM data.

    Returns:
        str: The encrypted data as a string.
    """
    data = (str(client_id) + "-" + str(scorm)).encode()
    base64_encoded_data = base64.b64encode(data)
    return base64_encoded_data.decode()


def decrypt_data(base64_encoded_data) -> str:
    """
    Decrypts the given Base64 encoded data.

    Args:
        base64_encoded_data (str): The Base64 encoded data to be decrypted.

    Returns:
        str: The decrypted plain text.

    """
    base64_decoded_data = base64.b64decode(base64_encoded_data)
    return base64_decoded_data.decode()


def replace_placeholders(temp_wrapper_dir, client_specific_data):
    """
    Replace placeholders in files within the extracted SCORM wrapper directory.
    """
    logger.info(f"Starting to replace placeholders in {temp_wrapper_dir}")
    logger.info(f"Client specific data: {client_specific_data}")

    def replace_placeholders_in_file(file_path, placeholders):
        logger.info(f"Starting to replace placeholders in {file_path}")
        if os.path.exists(file_path):
            logger.info(f"Path exists: {file_path}")
            with open(file_path, "r+") as file:
                contents = file.read()
                new_contents = contents
                for placeholder, value in placeholders.items():
                    if placeholder == "ID" and "configuration.js" in file_path:
                        new_contents = new_contents.replace(placeholder, value, 1)
                    else:
                        new_contents = new_contents.replace(placeholder, value)
                logger.info(f"New contents: {new_contents}")
                file.seek(0)
                file.write(new_contents)
                file.truncate()

    for root, dirs, files in os.walk(temp_wrapper_dir):
        for file in files:
            if file == "configuration.js":
                file_path = os.path.join(root, file)
                placeholders = {"ID": client_specific_data["id"]}
                replace_placeholders_in_file(file_path, placeholders)
            elif file == "imsmanifest.xml":
                file_path = os.path.join(root, file)
                placeholders = {"{{SCORM_TITLE}}": client_specific_data["scorm_title"]}
                replace_placeholders_in_file(file_path, placeholders)

def create_modified_scorm_wrapper(client_specific_data, assignment):
    """
    Create a modified SCORM wrapper with client-specific data and store it in the database.
    The zip file will contain the files directly in the root directory.
    """
    scorm_wrapper_path = os.path.join(settings.MEDIA_ROOT, "scorm_wrapper", "scorm-wrapper.zip")
    temp_dir = tempfile.mkdtemp()
    temp_wrapper_dir = os.path.join(temp_dir, "scorm_wrapper")
    with zipfile.ZipFile(scorm_wrapper_path, "r") as zip_ref:
        zip_ref.extractall(temp_wrapper_dir)
    replace_placeholders(temp_wrapper_dir, client_specific_data)
    archive_path = os.path.join(temp_dir, "modified_wrapper.zip")
    with zipfile.ZipFile(archive_path, "w") as zip_ref:
        for root, dirs, files in os.walk(temp_wrapper_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zip_ref.write(file_path, os.path.basename(file_path))  # Add files to the root of the zip

    # Create a unique filename using the client's id
    scorm_title = client_specific_data["scorm_title"].replace(" ", "_")  
    unique_filename = f"{scorm_title}_wrapper_{assignment.client.id}.zip"
    with open(archive_path, "rb") as file:
        assignment.client_scorm_file.save(unique_filename, File(file), save=True)
    shutil.rmtree(temp_dir)
    return assignment
