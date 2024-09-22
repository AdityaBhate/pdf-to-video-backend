# PDF Analysis and Storage Server

This Flask application processes uploaded PDF files, analyzes their content using OpenAI's GPT model, and stores the results in a MySQL database.

## Setup Instructions

1. Clone the repository and navigate to the server directory:

   ```
   git clone <repository-url>
   cd <repository-name>/server
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:

   - Copy the `.env.example` file to `.env`
   - Fill in the necessary values in the `.env` file

5. Ensure you have MySQL installed and running. Update the `DATABASE_URL` in the `.env` file with your MySQL connection string.

6. Run the Flask application:
   ```
   python main.py
   ```

The server should now be running on `http://localhost:5000`.

## API Endpoints

- `POST /upload-pdf`: Upload a PDF file for analysis and storage

## Important Notes

- Make sure you have a valid OpenAI API key set in the `.env` file.
- Ensure your MySQL database is properly configured and accessible.
- The application uses a temporary file to process PDFs. Ensure your server has write permissions in the directory where it's running.
