import bsdiff4
import os
import tempfile
import zipfile
import logging

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

key = Fernet.generate_key()


def encrypt_data(client_id, scorm) -> str:
    """
    Encrypts the given client ID and SCORM data.

    Args:
        client_id (int): The client ID.
        scorm (str): The SCORM data.

    Returns:
        str: The encrypted data as a string.
    """
    cipher_suite = Fernet(key)
    data = (str(client_id) + "-" + str(scorm)).encode()
    cipher_text = cipher_suite.encrypt(data)
    return cipher_text.decode()


def decrypt_data(cipher_text) -> str:
    """
    Decrypts the given cipher text using the Fernet encryption algorithm.

    Args:
        cipher_text (str): The encrypted text to be decrypted.

    Returns:
        str: The decrypted plain text.

    """
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(cipher_text.encode())
    return plain_text.decode()


def replace_placeholders(file_path, client_specific_data) -> None:
    """
    Replace placeholders in a file with client-specific data.

    Args:
        file_path (str): The path to the file.
        client_specific_data (dict): A dictionary containing client-specific data.

    Returns:
        None
    """
    if os.path.exists(file_path):
        logger.info(f"Opening file: {file_path}")
        with open(file_path, "r+") as file:
            contents = file.read()
            logger.info(
                f"Before replacement:\n{contents}"
            )  
            if "configuration.js" in file_path:
                logger.info("Replacing 'ID' in configuration.js")
                contents = contents.replace("ID", client_specific_data["id"], 1)
            elif "imsmanifest.xml" in file_path:
                logger.info("Replacing '{{SCORM_TITLE}}' in imsmanifest.xml")
                contents = contents.replace(
                    "{{SCORM_TITLE}}", client_specific_data["scorm_title"]
                )
            logger.info(
                f"After replacement:\n{contents}"
            )  
            file.seek(0)
            file.write(contents)
            file.truncate()
    else:
        logger.warning(f"The file {file_path} does not exist. Continuing execution.")


def generate_client_scorm_file(original_scorm_file, client_specific_data) -> str:
    """
    Generate a client-specific SCORM file by replacing placeholders in the original SCORM file.

    Args:
        original_scorm_file (str): The path to the original SCORM file.
        client_specific_data (dict): A dictionary containing client-specific data to replace the placeholders.

    Returns:
        str: The path to the generated client-specific SCORM file.
    """
    logger.info("Creating temporary directory")
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Extracting {original_scorm_file.path} to {temp_dir}")

    with zipfile.ZipFile(original_scorm_file.path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    replace_placeholders(
        os.path.join(temp_dir, "imsmanifest.xml"), client_specific_data
    )
    replace_placeholders(
        os.path.join(temp_dir, "configuration.js"), client_specific_data
    )

    client_scorm_file_path = tempfile.mktemp()
    logger.info(f"Creating client SCORM file at: {client_scorm_file_path}")

    with zipfile.ZipFile(client_scorm_file_path, "w") as zip_ref:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                zip_ref.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), temp_dir),
                )

    logger.info(f"Client SCORM file generated at: {client_scorm_file_path}")
    return client_scorm_file_path
