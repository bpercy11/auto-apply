import json
import os
import re
from openai import OpenAI
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def create_prompt(company_name, job_role_name, job_description_text):
    with open('input/resume.txt', 'r') as file:
        resume = file.read()

    with open('input/prompt.txt', 'r') as file:
        prompt = file.read()

    return prompt.format(resume=resume, company_name=company_name, role_name=job_role_name,
                         job_description=job_description_text)


def invoke_chatgpt(prompt):
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"{prompt}"}
            ]
        )
        result = completion.choices[0].message.content

        return result
    except Exception as e:
        print(f"ERROR: {str(e)}")


def interpolate_constants(input, config):
    current_date = datetime.now()
    formatted_date = current_date.strftime("%B %d, %Y")
    input = re.sub(r'\[Your Name\]', config.get('full-name'), input)
    input = re.sub(r'\[Your Address\]', config.get('street-address'), input)
    input = re.sub(r'\[City, State, Zip\]', config.get('city-state-zip'), input)
    input = re.sub(r'\[Email\]', config.get('email'), input)
    input = re.sub(r'\[Phone Number\]', config.get('phone'), input)
    input = re.sub(r'\[Date\]', formatted_date, input)

    return input


def save_to_file(result, company_name):
    with open(f"{company_name}-cover-letter.txt", "w") as text_file:
        text_file.write(result)


def output_pdf(cover_letter, job_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt=cover_letter, ln=1, align='C')
    pdf.output(f"{job_name}-cover-letter.pdf")


if __name__ == "__main__":
    try:
        with open('config.json') as file:
            config = json.load(file)

        os.environ['OPENAI_API_KEY'] = config.get('openai-api-key')

        company_name = input("Company name: ")
        job_role_name = input("Role name: ")
        job_description_url = input("Job description URL: ")

        if job_description_url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(job_description_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            job_description_text = soup.get_text(separator=' ', strip=True)

        prompt = create_prompt(company_name, job_role_name, job_description_text)
        result = invoke_chatgpt(prompt)
        # with open('test/gptoutput.txt', 'r') as file:
        #     result = file.read()
        result = interpolate_constants(result, config)
        save_to_file(result, company_name)
    except Exception as e:
        print(f"ERROR: {str(e)}")
