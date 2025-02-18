import json
import os
import re
from openai import OpenAI
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import tkinter as tk
from tkinter import ttk

SETTINGS_FILE = "config.json"


def save_settings(api_key, full_name, street_address, city_state_zip, email, phone):
    settings = {
        "openai-api-key": api_key,
        "full-name": full_name,
        "street-address": street_address,
        "city-state-zip": city_state_zip,
        "email": email,
        "phone": phone
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}


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
    try:
        current_date = datetime.now()
        formatted_date = current_date.strftime("%B %d, %Y")
        input = re.sub(r'\[Your Name\]', config.get('full-name'), input)
        input = re.sub(r'\[Your Address\]', config.get('street-address'), input)
        input = re.sub(r'\[City, State, Zip\]', config.get('city-state-zip'), input)
        input = re.sub(r'\[Email\]', config.get('email'), input)
        input = re.sub(r'\[Phone Number\]', config.get('phone'), input)
        input = re.sub(r'\[Date\]', formatted_date, input)

        return input

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return input


def save_to_file(result, company_name):
    try:
        with open(f"{company_name}-cover-letter.txt", "w") as text_file:
            text_file.write(result)
    except Exception as e:
        print(f"ERROR: {str(e)}")


def output_pdf(cover_letter, job_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt=cover_letter, ln=1, align='C')
    pdf.output(f"{job_name}-cover-letter.pdf")


def generate(settings, company_name, role_name, job_url):
    try:
        os.environ['OPENAI_API_KEY'] = settings.get('openai-api-key')
        if job_url:
            response = requests.get(job_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            job_description_text = soup.get_text(separator=' ', strip=True)

        prompt = create_prompt(company_name, role_name, job_description_text)
        # result = invoke_chatgpt(prompt)
        with open('test/gptoutput.txt', 'r') as file:
            result = file.read()
        result = interpolate_constants(result, settings)
        save_to_file(result, company_name)

    except Exception as e:
        print(f"ERROR: {str(e)}")


def open_settings(settings):
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    curr_api_key = tk.StringVar()
    curr_api_key.set(settings.get('openai-api-key'))
    api_key_label = ttk.Label(settings_window, text=f"OpenAI API key: ")
    api_key_label.grid(row=0, column=0, padx=10, pady=5)
    api_key_entry = ttk.Entry(settings_window, textvariable=curr_api_key)
    api_key_entry.grid(row=0, column=1, padx=10, pady=5)

    curr_full_name = tk.StringVar()
    curr_full_name.set(settings.get('full-name'))
    full_name_label = ttk.Label(settings_window, text=f"Full Name: ")
    full_name_label.grid(row=1, column=0, padx=10, pady=5)
    full_name_entry = ttk.Entry(settings_window, textvariable=curr_full_name)
    full_name_entry.grid(row=1, column=1, padx=10, pady=5)

    curr_street_address = tk.StringVar()
    curr_street_address.set(settings.get('street-address'))
    street_address_label = ttk.Label(settings_window, text=f"Street Address: ")
    street_address_label.grid(row=2, column=0, padx=10, pady=5)
    street_address_entry = ttk.Entry(settings_window, textvariable=curr_street_address)
    street_address_entry.grid(row=2, column=1, padx=10, pady=5)

    curr_city_state_zip = tk.StringVar()
    curr_city_state_zip.set(settings.get('city-state-zip'))
    city_state_zip_label = ttk.Label(settings_window, text=f"City, State, Zip: ")
    city_state_zip_label.grid(row=3, column=0, padx=10, pady=5)
    city_state_zip_entry = ttk.Entry(settings_window, textvariable=curr_city_state_zip)
    city_state_zip_entry.grid(row=3, column=1, padx=10, pady=5)

    curr_email = tk.StringVar()
    curr_email.set(settings.get('email'))
    email_label = ttk.Label(settings_window, text=f"Email: ")
    email_label.grid(row=4, column=0, padx=10, pady=5)
    email_entry = ttk.Entry(settings_window, textvariable=curr_email)
    email_entry.grid(row=4, column=1, padx=10, pady=5)

    curr_phone = tk.StringVar()
    curr_phone.set(settings.get('phone'))
    phone_label = ttk.Label(settings_window, text=f"Phone: ")
    phone_label.grid(row=5, column=0, padx=10, pady=5)
    phone_entry = ttk.Entry(settings_window, textvariable=curr_phone)
    phone_entry.grid(row=5, column=1, padx=10, pady=5)

    save_settings_button = ttk.Button(settings_window,
                                      text="Save",
                                      command=lambda:
                                        save_settings(api_key_entry.get(),
                                                      full_name_entry.get(),
                                                      street_address_entry.get(),
                                                      city_state_zip_entry.get(),
                                                      email_entry.get(),
                                                      phone_entry.get()))
    save_settings_button.grid(row=6, column=0, columnspan=2, pady=10)


root = tk.Tk()
root.title("Cover Letter Generator")

settings = load_settings()

company_name_label = ttk.Label(root, text=f'Company Name: ')
company_name_label.grid(row=0,column=0,padx=10,pady=5)
company_name_entry = ttk.Entry(root)
company_name_entry.grid(row=0,column=1,padx=10,pady=5)

role_name_label = ttk.Label(root, text=f'Role Name: ')
role_name_label.grid(row=1, column=0, padx=10, pady=5)
role_name_entry = ttk.Entry(root)
role_name_entry.grid(row=1, column=1, padx=10, pady=5)

job_url_label = ttk.Label(root, text=f'Job Description URL: ')
job_url_label.grid(row=2, column=0, padx=10, pady=5)
job_url_entry = ttk.Entry(root)
job_url_entry.grid(row=2, column=1, padx=10, pady=5)

generate_button = ttk.Button(root, text="Generate", command=lambda:
                                            generate(settings,
                                                     company_name_entry.get(),
                                                     role_name_entry.get(),
                                                     job_url_entry.get()))

generate_button.grid(row=3, column=0, columnspan=2, pady=10)

settings_button = ttk.Button(root, text="Settings", command=lambda: open_settings(settings))
settings_button.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
