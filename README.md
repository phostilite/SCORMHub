# SCORM Uploader for CloudSCORM

A Django-powered project to facilitate uploading SCORM packages to the CloudSCORM platform.

## Description

This project provides a user-friendly interface and backend logic to:

*   Upload SCORM packages in ZIP format
*   Securely interact with the CloudSCORM API
*   Store relevant SCORM asset information in a database

## Prerequisites

*   **Python 3.x** ([https://www.python.org/downloads/](https://www.python.org/downloads/))
*   **Basic understanding of Django is helpful**

## Getting Started

### 1. Project Setup

*   Clone or download this repository.
*   Navigate to the project directory: `cd scorm-uploader`

### 2. Virtual Environment (Recommended)

*   Create a virtual environment: `python -m venv env`
*   Activate the environment:
    *   **Windows:** `env\Scripts\activate`
    *   **macOS/Linux:** `source env/bin/activate`

### 3. Install Dependencies

*   `pip install -r requirements.txt`

### 4. Environment Variables (.env file)

*   Create a `.env` file at the project root.
*   Add your CloudSCORM credentials:

    ```
    API_URL=[https://cloudscorm.cloudnuv.com/api/v1/scorm](https://cloudscorm.cloudnuv.com/api/v1/scorm)
    API_TOKEN=your_api_token 
    ```

*   **IMPORTANT:** Add `.env` to your `.gitignore` file.

### 5. Tailwind CSS and Flowbite (Optional)

*   **CDN:** Include links in your HTML templates.
*   **Local Install:** Follow Tailwind CSS and Flowbite setup instructions.

### 6. Database Setup

*   `python manage.py makemigrations`
*   `python manage.py migrate`

### 7. Create Admin User

*   `python manage.py createsuperuser`

### 8. Run the Server

*   `python manage.py runserver`

### 9. Using the Application

*   Access the upload form (typically at  http://127.0.0.1:8000/coreadmin/upload-scorm/)
*   Fill in the form and submit a valid SCORM ZIP file. 

## Making API Calls

*   Refer to CloudSCORM's API documentation.
*   API interaction code is likely in your Django views (`views.py`).

## Additional Notes

*   Consider using a library like `python-dotenv` to load environment variables.
*   Implement robust error handling and user feedback mechanisms.

## Contributing 

*   If you find a bug or have an idea for a new feature, please feel free to open an issue or create a pull request!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 