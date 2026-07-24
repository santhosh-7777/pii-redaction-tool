# PII Redaction Tool

## Overview

This project automatically detects and redacts Personally Identifiable Information (PII) from Microsoft Word (.docx) documents while preserving the original document formatting.

The tool identifies and replaces sensitive information with realistic fake values while maintaining consistency throughout the document. For example, if the same person's name appears multiple times, it is always replaced with the same fake name.

## PII Types Supported

The tool detects and redacts the following PII types:

- Full Names
- Email Addresses
- Phone Numbers
- Company Names
- Physical/Mailing Addresses
- Social Security Numbers (SSNs)
- Credit Card Numbers
- Dates of Birth
- IP Addresses

## Approach

The project uses a hybrid approach combining regular expressions and Named Entity Recognition (NER).

Regular expressions are used to detect structured entities such as:

- Email addresses
- Phone numbers
- SSNs
- Credit card numbers
- Dates of birth
- IP addresses

Microsoft Presidio with spaCy's transformer-based NER model (`en_core_web_trf`) is used to detect:

- Person names
- Company names
- Addresses

Detected entities from both approaches are merged and overlapping detections are resolved before replacement.

Each detected entity is replaced with a realistic fake value generated using the Faker library. The same original value is always replaced with the same fake value throughout the document.

The final redacted document preserves the original formatting, including fonts, tables, spacing, and layout.

## Installation

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

Windows

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Download the transformer model.

```bash
python -m spacy download en_core_web_trf
```

## Running

Place the input document inside the `input` folder.

Run:

```bash
python main.py
```

Generated files will be saved inside the `output` folder.

## Output

The project generates:

- Redacted DOCX document
- Replacement log
- Evaluation report

## Tradeoffs

The hybrid approach provides high recall while reducing false positives.

Structured entities such as email addresses and phone numbers are detected very accurately using regex.

Addresses remain the most challenging entity because location names such as "Pune" or "Mumbai" may appear independently and should not always be treated as mailing addresses.

Some organization names may occasionally be detected as PII even when they are general document terms. These cases are reported for manual review.

## Technologies Used

- Python
- Microsoft Presidio
- spaCy
- en_core_web_trf
- Faker
- python-docx
