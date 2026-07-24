# PII Redaction Tool

## Overview

This project automatically detects and redacts Personally Identifiable Information (PII) from Microsoft Word (.docx) documents while preserving the original document formatting.

The tool identifies sensitive information such as names, email addresses, phone numbers, companies, and addresses, and replaces them with realistic fake values.

## Features

- Detects multiple types of PII
- Redacts text while preserving document formatting
- Uses both regex and Microsoft Presidio for detection
- Generates consistent fake replacements
- Produces a replacement log
- Includes an evaluation pipeline to measure detection performance

## PII Types Supported

- Person Names
- Email Addresses
- Phone Numbers
- Company Names
- Postal Addresses

## Project Structure

```
pii-redaction-tool/
│
├── src/
│   ├── detector.py
│   ├── fake_mapper.py
│   ├── models.py
│   ├── presidio_recognizer.py
│   ├── redact_docx.py
│   ├── redactor.py
│   └── regex_recognizers.py
│
├── eval/
│   ├── evaluate.py
│   └── ground_truth.json
│
├── input/
│   └── Red Herring Prospectus.docx
│
├── output/
│   ├── redacted_rhp.docx
│   ├── replacement_log.json
│   └── evaluation_report.json
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

## Technologies Used

- Python
- Microsoft Presidio
- spaCy
- Transformer-based Named Entity Recognition
- Regex
- python-docx
- Faker

## Installation

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

Windows

```bash
venv\Scripts\activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

Download the spaCy transformer model.

```bash
python -m spacy download en_core_web_trf
```

## Running the Project

Place the input document inside the `input` folder.

Run:

```bash
python main.py
```

The redacted document and reports will be generated inside the `output` folder.

## Output Files

The project generates:

- redacted_rhp.docx – Redacted document
- replacement_log.json – Original and replacement values
- evaluation_report.json – Evaluation results

## Evaluation

The project includes a manually annotated ground truth dataset.

Evaluation measures:

- Recall for each PII category
- Overall recall
- False positive candidates for manual review

The evaluation can be run using:

```bash
python eval/evaluate.py
```

## Approach

The system combines two detection methods.

Regex is used for structured entities such as:

- Email addresses
- Phone numbers

Microsoft Presidio with spaCy transformer models is used for:

- Person names
- Company names
- Addresses

Detected entities are merged, overlapping detections are resolved, and each entity is replaced with a consistent fake value generated using the Faker library.

Finally, the updated text is written back into the Word document while preserving the original formatting.

## Limitations

- Address detection is more challenging than other entity types.
- Some organization names may require manual review.
- Evaluation is performed on an annotated subset of the document rather than the entire document.

## Author

Piridi Santhosh Teja

National Institute of Technology Agartala

Email: santhosh.piridi123@gmail.com