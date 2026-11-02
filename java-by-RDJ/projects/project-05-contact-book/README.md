# Project 05 — File-Backed Contact Book

**Status:** ⬜ Not started · **Needs:** `03-collections`, `04-exceptions`, `07-file-io`

## 📌 Project Description

A console contact book that saves to disk and survives restarts, missing files, and corrupted files.

## 📋 Requirements
1. Add, view, search (by name and by partial phone number), edit, delete contacts
2. Contacts are saved to a CSV or JSON file on every change and loaded at startup
3. Duplicate detection (same name and phone) with a clear message
4. Import and export to a user-chosen file path
5. A corrupt line in the file is skipped and reported, never a crash
6. Missing file on first run creates an empty book

## Non-Functional Requirements
- Try-with-resources for every file handle
- Writes are safe: write to a temp file, then move it over the real one, so a crash cannot leave half a file
- Phone and email validation with `Pattern`/`Matcher`

## ✅ Definition of Done
- [ ] Source, `.md` walkthrough, requirements self-check table
- [ ] Sample data file in the repo and a deliberately corrupt one for testing
- [ ] A "what happens when..." table: missing file, empty file, unreadable file, bad line
