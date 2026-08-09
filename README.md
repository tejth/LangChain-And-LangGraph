# LangChain-And-LangGraph
<img width="1536" height="1024" alt="ChatGPT Image May 19, 2026, 07_50_55 AM" src="https://github.com/user-attachments/assets/38efa4f9-f281-4aca-944f-d26e023683f2" />
﻿                                        
  
  
# 🤖 End-to-End Generative AI Projects with Gemini, LangChain & LLMs

> A growing collection of practical, end-to-end Generative AI and LLM applications built with **Python, Google Gemini, LangChain, LangGraph, Groq, Streamlit, Vector Databases, and SQL**.

This repository contains a collection of hands-on Generative AI projects designed to explore how modern LLMs can be integrated into real-world applications.

Each project focuses on a different LLM application pattern — from conversational chatbots and document question answering to multimodal AI, RAG, Text-to-SQL, invoice extraction, and resume analysis.

🚧 **This repository is continuously evolving. More projects will be added soon.**

---

## 🚀 Projects Included

### 01. 🧠 Building End-to-End LLM & Large Image Model Application using Gemini
<img width="1918" height="852" alt="1" src="https://github.com/user-attachments/assets/80905a3b-cad1-4d38-9d88-435364376f20" />

A multimodal Generative AI application demonstrating how **Google Gemini** can process text and visual information.

**Key Concepts:**
- Google Gemini API
- Multimodal AI
- Large Language Models
- Image understanding
- Prompt engineering
- Streamlit
- Python

---

### 02. 💬 Conversational Q&A Chatbot using Gemini
<img width="1918" height="973" alt="2" src="https://github.com/user-attachments/assets/15ba7844-9e17-45c0-b820-c79d2bc7c0dd" />


A simple conversational chatbot powered by Google Gemini with a focus on maintaining conversation context and providing interactive responses.

**Key Concepts:**
- Google Gemini
- Conversational AI
- Chat history
- Prompt engineering
- Streamlit
- Python

---

### 03. 🧾 Multi-Language Invoice Extractor using Gemini
<img width="662" height="958" alt="3" src="https://github.com/user-attachments/assets/9261eba4-b464-49d0-8aed-ded926f0b6be" />


An AI-powered invoice assistant that allows users to upload invoices and ask questions about the extracted information.

The application can work with invoices written in different languages and answer questions such as:

- What is the invoice number?
- What is the invoice date?
- What is the total amount?
- What is the tax amount?
- Who is the customer?
- Who is the seller?
- What products are listed?

**Key Concepts:**
- Multimodal Gemini
- Document understanding
- PDF & image processing
- Multi-language understanding
- Information extraction
- Conversational Q&A
- Streamlit

---

### 04. 📚 Chat with Multiple PDF Documents using LangChain & Google Gemini
<img width="996" height="941" alt="5" src="https://github.com/user-attachments/assets/bfd03e12-adea-40ad-b88c-7946db71ee26" />


A document-based Q&A application that allows users to upload multiple PDF documents and ask questions across their content.

The project demonstrates the fundamentals of **Retrieval-Augmented Generation (RAG)**.

**Key Concepts:**
- LangChain
- Google Gemini
- RAG
- PDF document loading
- Recursive text splitting
- Embeddings
- Vector search
- FAISS
- Semantic retrieval
- Streamlit

**Workflow:**

```text
PDF Documents
      ↓
Document Loading
      ↓
Text Splitting
      ↓
Embeddings
      ↓
Vector Database
      ↓
Similarity Search
      ↓
Relevant Context
      ↓
Google Gemini
      ↓
```

### 05. 🗂️ End-to-End Document Q&A using Google Gemma & Groq
<img width="1197" height="972" alt="4" src="https://github.com/user-attachments/assets/bdcef72a-1446-4617-a0d8-0b851d8ba45b" />


An end-to-end **Document Question Answering application** built using **Google Gemma** and the **Groq API**.

The application allows users to work with documents and ask questions using natural language. Relevant information is retrieved from the documents and provided to the LLM to generate context-based answers.

#### ✨ Key Features

- 📄 Document-based Question Answering
- 🤖 Google Gemma LLM
- ⚡ Groq API for fast inference
- 🔎 Semantic Document Retrieval
- 🧠 Context-aware responses
- 💬 Natural-language interaction
- 🖥️ Streamlit interface

#### 🛠️ Technologies Used

- Python
- Google Gemma
- Groq API
- LangChain
- FAISS
- Embeddings
- Streamlit
- Python-dotenv

#### 🧠 Concepts Covered

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- Document Retrieval
- Semantic Search
- Vector Embeddings
- FAISS Vector Store
- Prompt Engineering
- Context-aware Question Answering
- Generative AI Application Development

#### 🔄 Application Workflow

```text
User Question
      ↓
Document Retrieval
      ↓
Relevant Context
      ↓
Google Gemma
      ↓
Groq API
      ↓
Generated Answer
```


### 06. 🗄️ End-to-End Text-to-SQL LLM Application using Gemini
<img width="1918" height="972" alt="7" src="https://github.com/user-attachments/assets/535b99f1-9695-4f95-a953-891fbb045551" />


An end-to-end **Text-to-SQL application** that allows users to interact with a SQL database using natural language.

Instead of writing SQL queries manually, users can simply ask questions in English. Google Gemini understands the question, generates the appropriate SQL query, executes it against the database, and returns the result.

For example:

> "How many students are in the 10th class?"

The application can convert the question into an SQL query such as:

```sql
SELECT COUNT(*)
FROM STUDENT
WHERE CLASS = '10th';
```



---

### 07. 📄 End-to-End ATS Resume Analyzer using Gemini Vision
<img width="1913" height="1027" alt="8" src="https://github.com/user-attachments/assets/7bd7a322-e4ff-440f-bd83-49254180954f" />


An end-to-end **Applicant Tracking System (ATS) Resume Analyzer** built using Google's Gemini multimodal AI capabilities.

This application allows users to enter a **Job Description** and upload their **Resume**. Gemini analyzes the resume against the job requirements and provides useful insights about the candidate's compatibility with the target role.

The application also allows users to ask questions related to their uploaded resume.

#### ✨ Key Features

- 📄 Upload Resume
- 📋 Enter Job Description
- 🤖 AI-powered Resume Analysis
- 🎯 ATS Compatibility Analysis
- 📊 Resume & Job Description Matching
- 🔑 Keyword Matching
- ❌ Missing Keyword Detection
- 🛠️ Technical Skill Gap Analysis
- 💼 Relevant Experience Analysis
- 💪 Resume Strength Identification
- ⚠️ Resume Weakness Identification
- 💡 Resume Improvement Suggestions
- 💬 Ask Questions About the Resume
- 🖥️ Interactive Streamlit Interface

#### 🛠️ Technologies Used

- Python
- Google Gemini API
- Google GenAI SDK
- Gemini Vision / Multimodal AI
- Streamlit
- PDF Processing
- Python-dotenv
- Prompt Engineering

#### 🧠 Concepts Covered

- Multimodal Generative AI
- Gemini Vision
- Large Language Models
- Resume Intelligence
- Applicant Tracking Systems (ATS)
- Resume-Job Description Matching
- Keyword Analysis
- Skill Gap Analysis
- Document Understanding
- Prompt Engineering
- AI-powered Resume Analysis

#### 🔄 Application Workflow

```text
                Job Description
                       +
                    Resume
                       ↓
              Gemini Multimodal AI
                       ↓
              Resume Understanding
                       ↓
          Job Description Understanding
                       ↓
               Resume Comparison
                       ↓
          ┌────────────┴────────────┐
          ↓                         ↓
   Matching Skills            Missing Skills
          ↓                         ↓
 Matching Keywords          Missing Keywords
          └────────────┬────────────┘
                       ↓
                 ATS Analysis
                       ↓
              Resume Score & Insights
                       ↓
              Improvement Suggestions
```




