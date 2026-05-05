# GraphRAG Syllabus Project

This project implements a GraphRAG-based pipeline to construct a knowledge graph from university course syllabi. The system extracts structured information from PDF documents using a local large language model, converts the extracted data into graph triples, enriches the graph with career-based links, stores the graph in Neo4j, and supports question answering over the constructed graph.

--------------------------------------------------

## Execution Pipeline

The project should be executed in the following order:

python main.py  
python build_links.py  
python neo4j_store.py  
python ask.py  

--------------------------------------------------

## Installation

Create a virtual environment:

python3 -m venv venv  
source venv/bin/activate  

Install required dependencies:

pip install -r requirements.txt  

--------------------------------------------------

## System Requirements

### Ollama (Local LLM)

The project uses a local LLM via Ollama for structured information extraction.

Install and run the model:

ollama pull llama3.1  
ollama run llama3.1  

The model is defined in the code as:

MODEL_NAME = "llama3.1"

--------------------------------------------------

### Neo4j Database

Ensure Neo4j is running locally.

Default connection configuration:

NEO4J_URI = "bolt://localhost:7687"  
NEO4J_USERNAME = "neo4j"  
NEO4J_PASSWORD = "password123"  

--------------------------------------------------

## Project Structure

data/  
 ├── syllabi/       PDF syllabus files  
 └── careers/       Career definitions  

outputs/  
 ├── texts/         Extracted raw text  
 ├── json/          Structured syllabus data  
 └── triples/       Knowledge graph triples  

main.py  
build_links.py  
neo4j_store.py  
ask.py  
qa.py  
pdf_reader.py  
llm_extractor.py  
kg_builder.py  
linker.py  
evaluate.py  
requirements.txt  

--------------------------------------------------

## Pipeline Description

### main.py

This script executes the main pipeline.

Steps performed:

- Reads PDF files from data/syllabi/  
- Extracts text content from PDFs  
- Sends text to the local LLM  
- Extracts structured information such as:
  - course code
  - course title
  - prerequisites
  - corequisites
  - topics
  - learning outcomes  
- Saves structured data as JSON  
- Converts JSON into graph triples  
- Stores outputs in the outputs directory  

--------------------------------------------------

### build_links.py

This script enriches the graph by creating semantic links between:

- careers  
- topics  
- courses  

The linking logic is based on topic matching.

Examples of relations:

Career -> REQUIRES_TOPIC -> Topic  
Topic -> TAUGHT_IN -> Course  
Career -> RECOMMENDED_COURSE -> Course  

Output file:

outputs/triples/career_linked_triples.json  

--------------------------------------------------

### neo4j_store.py

This script inserts all triples into the Neo4j database.

Important behavior:

- The database is cleared before insertion  
- All nodes and relationships are recreated  

--------------------------------------------------

### ask.py

This script provides an interactive question-answering interface.

Run:

python ask.py  

Example questions:

What are the prerequisites of CS515?  
What are the topics of CS515?  
Recommend courses for Data Scientist  

--------------------------------------------------

## File Responsibilities

pdf_reader.py  
Extracts text from PDF files.

llm_extractor.py  
Uses the local LLM to convert raw text into structured JSON.

kg_builder.py  
Transforms structured JSON into graph triples.

linker.py  
Creates connections between careers, topics, and courses.

qa.py  
Maps user questions to Cypher queries and retrieves results from Neo4j.

evaluate.py  
Evaluates the question-answering system using predefined test cases.

--------------------------------------------------

## Example Execution

source venv/bin/activate  

python main.py  
python build_links.py  
python neo4j_store.py  
python ask.py  

--------------------------------------------------

## Notes

- Neo4j must be running before executing neo4j_store.py and ask.py  
- Ollama must be running before executing main.py  
- Running neo4j_store.py overwrites the existing graph in Neo4j  
- The question answering system is rule-based and relies on predefined query patterns  

--------------------------------------------------
