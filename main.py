from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
from sqlalchemy import create_engine, Column, Integer, String, JSON, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json
import pymysql
import tempfile
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class PDFContent(Base):
    __tablename__ = 'pdf_information'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    summary = Column(Text)
    segments = Column(JSON)
    tone = Column(Text)


Base.metadata.create_all(engine)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_image(segment):
    return "image_url"


def summarize_and_segment(text, filename):
    print("Starting summarization and segmentation...")
    prompt = f"""Analyze the following text from a PDF file named "{filename}" and provide the following information in JSON format:
    1. A suitable title for a video based on this content
    2. A comprehensive summary of the text
    3. Logical segments of the content (either based on pages or other logical divisions)
    4. The overall tone of the document in one or two words

    Return the information in the following JSON structure:
    {{
        "title": "Video title based on the content",
        "summary": "Comprehensive summary of the text",
        "segments": [
            {{"title": "Segment title", "content": "Summarized content of the segment"}}
        ],
        "tone": "One-line description of the overall tone less than 250 characters"
    }}

    Text to analyze:
    {text}

    IMPORTANT: Return ONLY the JSON object. Do not include any additional text or explanations.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes and summarizes text for video production. You must return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    print("Received response from OpenAI")
    try:
        result = json.loads(response.choices[0].message.content)
        print("Successfully parsed OpenAI response as JSON")
        return result
    except json.JSONDecodeError:
        print(response.choices[0].message.content)
        print("Error: OpenAI response is not valid JSON")
        raise ValueError("OpenAI response is not valid JSON")

# Generate image from the each segement


@ app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    print("Received PDF upload request")
    if 'file' not in request.files:
        print("Error: No file part in the request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        print("Error: No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        print(f"Processing file: {filename}")

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            print(f"Saved temporary file: {temp_file_path}")

            with open(temp_file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                full_text = ""

                for page_num, page in enumerate(pdf_reader.pages):
                    full_text += page.extract_text() + "\n\n"
                    print(f"Extracted text from page {page_num + 1}")

                print("Starting OpenAI analysis")
                analyzed_content = summarize_and_segment(full_text, filename)

                print("Storing analyzed content in database")
                session = Session()
                pdf_content = PDFContent(
                    title=analyzed_content['title'],
                    summary=analyzed_content['summary'],
                    segments=json.dumps(analyzed_content['segments']),
                    tone=analyzed_content['tone']
                )
                session.add(pdf_content)
                session.commit()
                print("Successfully stored in database")

            os.unlink(temp_file_path)
            print(f"Removed temporary file: {temp_file_path}")
            return jsonify({'message': 'PDF uploaded, analyzed, and stored successfully'}), 200

        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return jsonify({'error': str(e)}), 500

    print("Error: Invalid file format")
    return jsonify({'error': 'Invalid file format'}), 400


if __name__ == '__main__':
    app.run(debug=True)
