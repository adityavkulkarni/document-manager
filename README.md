# Document Manager

**A modern, robust, and fun Flask API for managing PDFs and their related files, with support for both HDFS and local file systems.**

## 🚀 Overview

Document Manager is a Python & Flask REST API designed to make PDF document management effortless and scalable. Whether you're storing research papers, contracts, or any document with related files (like images or attachments), this project has you covered. Backed by PostgreSQL (or SQLite), it supports both local and Hadoop (HDFS) file storage, making it suitable for everything from personal projects to enterprise data lakes.

## ✨ Features

- **Upload PDFs**: Store your PDF documents with automatic metadata extraction.
- **Attach Related Files**: Link images, spreadsheets, or any file to your PDFs.
- **Flexible Storage**: Choose between local file storage or distributed HDFS.
- **RESTful API**: Clean, well-structured endpoints for all operations.
- **Sophisticated UI**: Upload, view, and manage documents from a friendly web interface.
- **Filter & Search**: Query documents and attachments by name or metadata.
- **Download & Delete**: Retrieve or remove documents and attachments with ease.
- **Extensible**: Built with Flask, SQLAlchemy, and Marshmallow for easy customization.

## 🏗️ Architecture

| Component      | Description                                  |
|----------------|----------------------------------------------|
| Flask API      | REST endpoints for all document operations    |
| SQLAlchemy     | ORM for PostgreSQL/SQLite metadata storage    |
| HDFS/LocalFS   | Pluggable file storage backend                |
| Marshmallow    | Schema validation and serialization           |
| UI             | Simple web interface (Flask templates)        |

## 🔧 Quickstart

### 1. Clone the Repo

```bash
git clone https://github.com/adityavkulkarni/document-manager.git
cd document-manager
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file (or set environment variables):

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/document_manager
PARENT_DIRECTORY=uploads
FILE_SYSTEM=local  # or 'hadoop'
HADOOP_NAMENODE_URL=http://namenode:9870
HADOOP_USERNAME=hadoop
```

### 4. Run the App

```bash
flask run
```

Or with Docker Compose:

```bash
docker-compose up
```

## 📚 API Endpoints

| Method | Endpoint                                    | Description                      |
|--------|---------------------------------------------|----------------------------------|
| POST   | `/api/pdfs/`                                | Upload a new PDF                 |
| GET    | `/api/pdfs/`                                | List PDFs (filter by name/meta)  |
| GET    | `/api/pdfs/<pdf_id>`                        | Get PDF metadata                 |
| GET    | `/api/pdfs/download/<pdf_id>`               | Download PDF file                |
| DELETE | `/api/pdfs/<pdf_id>`                              | Delete PDF and attachments       |
| POST   | `/api/attachments/`                         | Upload related file to a PDF     |
| GET    | `/api/attachments/`                         | List attachments (filterable)    |
| GET    | `/api/attachments/<attachment_id>`          | Get attachment metadata          |
| GET    | `/api/attachments/download/<attachment_id>` | Download attachment file         |
| DELETE | `/api/attachments/<attachment_id>`          | Delete attachment                |

## 🖥️ Web UI

- **Home:** Browse all PDFs, upload new documents, and view details.
- **PDF View:** See metadata, download the PDF, and manage related files.
- **Upload Forms:** Add PDFs or related files with optional metadata.

## 🏄 Usage Example

```python
from DocumentManagerClient import DocumentManagerClient

client = DocumentManagerClient("http://localhost:7575")

# Upload a PDF
pdf = client.upload_pdf("example.pdf", metadata='{"author": "Jane Doe"}')

# List PDFs
pdfs = client.list_pdfs()

# Upload an attachment
attachment = client.upload_attachment(pdf['id'], "image.jpg", metadata='{"type": "cover"}')
```

## 🛠️ File System Support

- **LocalFS**: Default for quick setup and development.
- **HDFS**: For big data and distributed storage—just set `FILE_SYSTEM=hadoop` and configure your Hadoop connection.

## 🧩 Extending & Customizing

- Add new file types by updating `ALLOWED_EXTENSIONS` in `config.py`.
- Swap out the database or add authentication with minimal changes.
- Build on top of the REST API for integrations or automation.
