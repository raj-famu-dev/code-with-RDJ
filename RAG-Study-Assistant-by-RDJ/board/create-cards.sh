#!/usr/bin/env bash
# Adds the planned cards to the GitHub Project board as draft items.
# Needs the GitHub CLI (gh) logged in with the "project" scope:
#   gh auth refresh -s project
# Not run yet: review the cards first, then run:  bash board/create-cards.sh
set -euo pipefail
OWNER="raj-famu-dev"
NUMBER=4

add() { gh project item-create "$NUMBER" --owner "$OWNER" --title "$1" --body "$2"; }

add "[R0] Choose the notes to index and list them in data/" "Milestone R0: Scope and corpus. Label: docs. Target date: Jan 17, 2027. Proof of done for the milestone: Corpus list and 30 questions committed."
add "[R0] Write 30 sample questions with expected source notes" "Milestone R0: Scope and corpus. Label: eval. Target date: Jan 17, 2027. Proof of done for the milestone: Corpus list and 30 questions committed."
add "[R1] Write a loader for Markdown and PDF files" "Milestone R1: Ingestion and chunking. Label: ingest. Target date: Jan 31, 2027. Proof of done for the milestone: Ingest script and tests; chunk stats printed."
add "[R1] Implement overlapping chunking with file and heading metadata" "Milestone R1: Ingestion and chunking. Label: ingest. Target date: Jan 31, 2027. Proof of done for the milestone: Ingest script and tests; chunk stats printed."
add "[R1] Add tests and print chunk statistics" "Milestone R1: Ingestion and chunking. Label: ingest. Target date: Jan 31, 2027. Proof of done for the milestone: Ingest script and tests; chunk stats printed."
add "[R2] Choose an embedding model and vector index" "Milestone R2: Embeddings and retrieval baseline. Label: retrieval. Target date: Feb 14, 2027. Proof of done for the milestone: Search demo returning ranked chunks with scores."
add "[R2] Index all chunks and build top-k search" "Milestone R2: Embeddings and retrieval baseline. Label: retrieval. Target date: Feb 14, 2027. Proof of done for the milestone: Search demo returning ranked chunks with scores."
add "[R2] Demo: question in, ranked chunks with scores out" "Milestone R2: Embeddings and retrieval baseline. Label: retrieval. Target date: Feb 14, 2027. Proof of done for the milestone: Search demo returning ranked chunks with scores."
add "[R3] Write the grounded-answer prompt with citation format" "Milestone R3: Cited answers. Label: llm. Target date: Feb 28, 2027. Proof of done for the milestone: Transcript of 10 answers with citations plus 5 refusals."
add "[R3] Add a 'not found' path for out-of-scope questions" "Milestone R3: Cited answers. Label: llm. Target date: Feb 28, 2027. Proof of done for the milestone: Transcript of 10 answers with citations plus 5 refusals."
add "[R3] Save a transcript of 10 answers and 5 refusals" "Milestone R3: Cited answers. Label: docs. Target date: Feb 28, 2027. Proof of done for the milestone: Transcript of 10 answers with citations plus 5 refusals."
add "[R4] Grow the labelled set to 50+ questions" "Milestone R4: Evaluation set and metrics. Label: eval. Target date: Mar 21, 2027. Proof of done for the milestone: Results table and method committed in eval/."
add "[R4] Script: retrieval hit rate @k" "Milestone R4: Evaluation set and metrics. Label: eval. Target date: Mar 21, 2027. Proof of done for the milestone: Results table and method committed in eval/."
add "[R4] Script: answer correctness and citation accuracy" "Milestone R4: Evaluation set and metrics. Label: eval. Target date: Mar 21, 2027. Proof of done for the milestone: Results table and method committed in eval/."
add "[R4] Publish results table and method" "Milestone R4: Evaluation set and metrics. Label: docs. Target date: Mar 21, 2027. Proof of done for the milestone: Results table and method committed in eval/."
add "[R5] FastAPI app with /ask and /health" "Milestone R5: FastAPI service and tests. Label: api. Target date: Apr 4, 2027. Proof of done for the milestone: Service runs locally; tests pass."
add "[R5] pytest tests for the API" "Milestone R5: FastAPI service and tests. Label: api. Target date: Apr 4, 2027. Proof of done for the milestone: Service runs locally; tests pass."
add "[R6] Write the failure analysis and fix the top failure" "Milestone R6: Failure analysis, demo and write-up. Label: eval. Target date: Apr 18, 2027. Proof of done for the milestone: Failure section, demo clip and published write-up URL."
add "[R6] Record a short demo clip" "Milestone R6: Failure analysis, demo and write-up. Label: docs. Target date: Apr 18, 2027. Proof of done for the milestone: Failure section, demo clip and published write-up URL."
add "[R6] Publish the technical write-up" "Milestone R6: Failure analysis, demo and write-up. Label: docs. Target date: Apr 18, 2027. Proof of done for the milestone: Failure section, demo clip and published write-up URL."
