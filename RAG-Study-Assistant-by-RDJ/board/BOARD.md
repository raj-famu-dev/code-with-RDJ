# Project Board: RAG Study Assistant

Board: https://github.com/users/raj-famu-dev/projects/4

**Suggested columns:** Backlog → Ready → In Progress → In Review → Done

Every card starts in **Backlog**. Move a card to **Done** only when its proof is committed.

**Suggested labels:** `ingest`, `retrieval`, `llm`, `eval`, `api`, `docs`

## R0: Scope and corpus
Target: Jan 17, 2027

- [ ] **Choose the notes to index and list them in data/**  
  Label: `docs` · Milestone: R0 · Target date: Jan 17, 2027
- [ ] **Write 30 sample questions with expected source notes**  
  Label: `eval` · Milestone: R0 · Target date: Jan 17, 2027

## R1: Ingestion and chunking
Target: Jan 31, 2027

- [ ] **Write a loader for Markdown and PDF files**  
  Label: `ingest` · Milestone: R1 · Target date: Jan 31, 2027
- [ ] **Implement overlapping chunking with file and heading metadata**  
  Label: `ingest` · Milestone: R1 · Target date: Jan 31, 2027
- [ ] **Add tests and print chunk statistics**  
  Label: `ingest` · Milestone: R1 · Target date: Jan 31, 2027

## R2: Embeddings and retrieval baseline
Target: Feb 14, 2027

- [ ] **Choose an embedding model and vector index**  
  Label: `retrieval` · Milestone: R2 · Target date: Feb 14, 2027
- [ ] **Index all chunks and build top-k search**  
  Label: `retrieval` · Milestone: R2 · Target date: Feb 14, 2027
- [ ] **Demo: question in, ranked chunks with scores out**  
  Label: `retrieval` · Milestone: R2 · Target date: Feb 14, 2027

## R3: Cited answers
Target: Feb 28, 2027

- [ ] **Write the grounded-answer prompt with citation format**  
  Label: `llm` · Milestone: R3 · Target date: Feb 28, 2027
- [ ] **Add a 'not found' path for out-of-scope questions**  
  Label: `llm` · Milestone: R3 · Target date: Feb 28, 2027
- [ ] **Save a transcript of 10 answers and 5 refusals**  
  Label: `docs` · Milestone: R3 · Target date: Feb 28, 2027

## R4: Evaluation set and metrics
Target: Mar 21, 2027

- [ ] **Grow the labelled set to 50+ questions**  
  Label: `eval` · Milestone: R4 · Target date: Mar 21, 2027
- [ ] **Script: retrieval hit rate @k**  
  Label: `eval` · Milestone: R4 · Target date: Mar 21, 2027
- [ ] **Script: answer correctness and citation accuracy**  
  Label: `eval` · Milestone: R4 · Target date: Mar 21, 2027
- [ ] **Publish results table and method**  
  Label: `docs` · Milestone: R4 · Target date: Mar 21, 2027

## R5: FastAPI service and tests
Target: Apr 4, 2027

- [ ] **FastAPI app with /ask and /health**  
  Label: `api` · Milestone: R5 · Target date: Apr 4, 2027
- [ ] **pytest tests for the API**  
  Label: `api` · Milestone: R5 · Target date: Apr 4, 2027

## R6: Failure analysis, demo and write-up
Target: Apr 18, 2027

- [ ] **Write the failure analysis and fix the top failure**  
  Label: `eval` · Milestone: R6 · Target date: Apr 18, 2027
- [ ] **Record a short demo clip**  
  Label: `docs` · Milestone: R6 · Target date: Apr 18, 2027
- [ ] **Publish the technical write-up**  
  Label: `docs` · Milestone: R6 · Target date: Apr 18, 2027

