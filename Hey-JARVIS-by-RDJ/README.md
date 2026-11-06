<div align="center">

<img src="assets/banner.svg" alt="Hey-JARVIS-by-RDJ: a voice waveform pulsing beside the wake phrase Hey, JARVIS" width="100%"/>

<br/>

![Focus](https://img.shields.io/badge/Focus-Voice%20AI%20Assistant-7C3AED?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Stages](https://img.shields.io/badge/Stages%20Built-0%20of%205-6B7280?style=for-the-badge)
![Inspiration](https://img.shields.io/badge/Inspired%20by-Fictional%20AI-DC2626?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Concept%20Only-yellow?style=for-the-badge)
[![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)](https://github.com/raj-famu-dev)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

### *Say it. Understand it. Act on it. Measure it.*

[About](#-about) •
[Interface](#-interface-concept) •
[Definition](#-what-is-jarvis) •
[Goal](#-the-goal) •
[Pipeline](#-pipeline) •
[Learn](#-what-to-learn) •
[Roadmap](#-roadmap-and-deadlines) •
[Progress](#-progress) •
[Principles](#-design-principles) •
[Integrity](#-integrity-and-naming) •
[Structure](#-structure) •
[Log](#-progress-log)

</div>

---

## 👋 About

This is **Raj Patel's** ("RDJ") plan for a personal, voice-first AI assistant, built as a Computer Science student at Florida A&M University. The idea is simple: say "Hey, JARVIS", ask for something, and get a useful spoken answer.

**Today this folder holds the plan and nothing else.** There is no code, no demo and no result yet. This README exists so the design is public before the work is, and each stage is marked done only when it runs and has proof.

---

## 🖥️ Interface Concept

<div align="center">
<img src="assets/hud.svg" alt="Animated mockup of the planned assistant dashboard: rotating rings around a listening core, stage indicators, gauges, a scrolling audio graph and a console log." width="100%"/>
</div>

An **animated mockup** of the dashboard I want to build around the assistant: a listening core, the five pipeline stages lighting up in turn, load gauges, a live microphone view, a console of what the assistant just did, and the allow-listed tools it may use. It is a design sketch only. **Nothing in it is real data or a working interface**, and the evaluation numbers on the left read `--` until a program measures them.

---

## 📖 What is JARVIS?

**JARVIS** stands for **"Just A Rather Very Intelligent System"**. It is a **fictional** artificial intelligence from the Marvel Cinematic Universe, created by the character **Tony Stark / Iron Man**.

| | |
|---|---|
| **What it is** | A fictional AI assistant that runs Stark's home, lab and suits |
| **How it's used** | Spoken natural language, started with "Hey, JARVIS" |
| **Personality** | Calm, polite and dry-witted |
| **Voiced by** | Paul Bettany |
| **Played Tony Stark** | Robert Downey Jr. (the actor, not the author of any real software) |

JARVIS is **not** a real product, and it was **not** made by Robert Downey Jr. This project is **not** affiliated with, endorsed by or connected to him, Marvel or Disney. "RDJ" in this repository's folder names is **Raj Patel**.

---

## 🎯 The Goal

Build an **original** assistant that borrows the *idea* of JARVIS and is judged like any other AI system: by measured results.

- **Real engineering:** speech, language model, tools and evaluation, all written and explained by me.
- **Measured, not claimed:** an evaluation set with metrics and failure cases, because a demo is not evidence.
- **Safe by default:** it acts only on my own machine, through an explicit allow-list.
- **Honest about scope:** it will never be the movie JARVIS, and this README will not pretend otherwise.

---

## 🧭 What a Reviewer Can Verify

- **Origin is disclosed:** the fictional source is named, and no Marvel material is copied.
- **Status is honest:** every stage below is ⬜ until it runs and has proof.
- **Nothing is overclaimed:** no skill level, accuracy or latency figure appears until a program prints it.
- **Own machine only:** no component will be pointed at systems I do not own.

---

## 🔬 Pipeline

<div align="center">
<img src="assets/pipeline.svg" alt="Five planned stages: wake, listen, think, act, speak. None built yet." width="100%"/>
</div>

1. **Wake:** a keyword spotter listens for "Hey, JARVIS" and ignores everything else.
2. **Listen:** speech-to-text turns the request into text.
3. **Think:** a language model with a defined persona and short-term memory decides what to do.
4. **Act:** it can call a small set of **allow-listed** tools (time, notes, file search, safe local commands).
5. **Speak:** text-to-speech reads the answer back.

---

## 📈 Progress

| # | Stage | Planned proof | Status |
|:-:|---|---|:-:|
| 1 | Wake phrase detection | Recorded test clips with hit and false-trigger counts | ⬜ Not Started |
| 2 | Speech-to-text and text-to-speech | Round-trip demo with word error rate on a small clip set | ⬜ Not Started |
| 3 | LLM conversation with a persona | Persona prompt in the repo plus sample transcripts | ⬜ Not Started |
| 4 | Allow-listed tools | Unit tests, including requests that must be refused | ⬜ Not Started |
| 5 | Evaluation set | Method, metrics and failure cases published here | ⬜ Not Started |

**Status key:** ✅ completed (runs, has proof) · 🔄 in progress · ⬜ not started

**Prerequisite:** the Python and FastAPI work in [`python-by-RDJ`](../python-by-RDJ/README.md). This project starts after it, as part of the [`ai-engineering-by-RDJ`](../ai-engineering-by-RDJ/README.md) track.

---

## 🧠 What to Learn

Five parts chained together. Build them in this order; the full dates are in the [roadmap project](./projects/project-01-roadmap-and-deadlines/README.md).

### 1. Python and audio basics
- Python fundamentals, virtual environments and packages
- Microphone and speakers: `sounddevice` or `PyAudio`, sample rates, audio as NumPy arrays
- Threads or `asyncio`, so it can listen while it works

### 2. Wake word detection ("Hey, JARVIS")
- How keyword spotting works: a small always-on model running on-device
- Options: openWakeWord (free), Picovoice Porcupine (free tier); a custom phrase can be trained
- The trade-off to measure: hit rate vs. false triggers

### 3. Speech-to-text (STT)
- Voice activity detection to know when I stop talking (Silero VAD, `webrtcvad`)
- Whisper run locally with `faster-whisper`, or a cloud STT API
- Word error rate (WER), the metric used to measure it

### 4. The brain: an LLM
- Calling an LLM API (Anthropic, OpenAI) or a local model through Ollama
- Prompt design: system prompt, persona, replies short enough to speak
- Conversation memory: history, trimming, optional stored notes
- **Tool calling / function calling**, the most important concept: how the model asks my code to do things such as check the time or search files

### 5. Tools and safety
- Small, well-tested Python functions the model can call
- Allow-list design, input validation, confirmation before anything destructive
- `subprocess` safety: never pass raw model output to a shell
- Logging every request and action

### 6. Text-to-speech (TTS)
- Quick start: `pyttsx3`. Better quality: Piper (local) or a cloud TTS API
- Streaming, so the reply starts before the full answer is ready

### 7. Evaluation and engineering
- Testing with `pytest`, including requests that must be refused
- A small test set measuring wake hit rate, WER, tool-call accuracy and end-to-end latency
- FastAPI, if a web or phone front end is added later

**Build order:** typed version first (text in, LLM and tools, text out), then TTS, then STT, and the wake word last. The hard logic should work before audio makes debugging harder.

---

## 🗓️ Roadmap and Deadlines

The separate planning project is [`project-01-roadmap-and-deadlines`](./projects/project-01-roadmap-and-deadlines/README.md): 8 milestones from **Nov 5, 2026** to a target finish of **Mar 14, 2027**, each with tasks and a proof of done. The dates are targets and will be edited honestly when they slip.

| Milestone | Deadline |
|---|---|
| M0 Foundation | Nov 22, 2026 |
| M1 Typed assistant | Dec 6, 2026 |
| M2 Tools and safety | Dec 20, 2026 |
| M3 Text-to-speech | Jan 3, 2027 |
| M4 Speech-to-text and VAD | Jan 24, 2027 |
| M5 Wake word | Feb 7, 2027 |
| M6 Evaluation set and results | Feb 28, 2027 |
| M7 Polish, demo and write-up | Mar 14, 2027 |

---

## 🛡️ Design Principles

1. **Allow-list, never deny-list:** the assistant can run only commands I have explicitly named.
2. **Confirm before anything destructive:** deleting, sending or spending needs a spoken or typed yes.
3. **Local first:** keep audio on my machine where possible, and say plainly what leaves it.
4. **Everything logged:** each request, tool call and result is recorded so it can be audited.
5. **Test the refusals:** the evaluation set includes requests the assistant must decline.

---

## ⚖️ Integrity and Naming

- **Fictional source:** the name, the acronym and the concept belong to Marvel. They are used here only as inspiration and a nod to the films.
- **Original work:** all code, prompts and any voice will be written by me or licensed, with sources stated. No film scripts, audio, logos or artwork will be copied in.
- **Honest comparison:** nothing here claims to match, replace or be the fictional JARVIS.

---

## 📂 Structure

Planned layout (only `README.md`, `LICENSE`, `assets/` and the roadmap project exist today):

```text
Hey-JARVIS-by-RDJ/
├── README.md          this file
├── LICENSE            MIT
├── assets/            banner, pipeline and interface-concept animations
├── projects/          project-01-roadmap-and-deadlines (milestones and dates)
├── src/               (planned) wake, speech, assistant, tools
├── tests/             (planned) unit tests and refusal tests
└── eval/              (planned) evaluation set and results
```

---

## 📈 Progress Log

- **November 5, 2026:** ⬜ Concept defined: README, naming and integrity notes, pipeline plan, learning list, and the roadmap project with 8 dated milestones. No code yet.

- **November 6, 2026:** ⬜ Added the animated interface concept (`assets/hud.svg`) and an animated pipeline. Design only; still no code.

*This log is updated after every session, not just when something impressive happens, to keep the record honest.*

---

## 🔥 A Note to Whoever Is Reading This

If you're a recruiter, a hiring manager or a fellow engineer: thank you for taking the time. This is an idea I'm excited about, and I'd rather show you an honest plan than a polished claim. When a stage turns green, there will be code you can run and numbers you can check.

— Raj Patel (RDJ), Tallahassee, Florida

## 🔗 Related Labs

| Lab | What it covers |
|---|---|
| 🤖 [AI Engineering](../ai-engineering-by-RDJ/README.md) | The track this project belongs to: services, RAG, agents and evaluation. |
| 🐍 [Python Lab](../python-by-RDJ/README.md) | The language this project will be written in. |
| 🛡️ [Cybersecurity](../cybersecurity-by-RDJ/README.md) | Own systems and legal labs only, the same rule this assistant follows. |

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev) · Instagram [`@rdj_369`](https://instagram.com/rdj_369)

<sub>Status: concept only. No code yet; this README exists so the plan is public before the work is. JARVIS is a fictional character owned by Marvel; this project is unaffiliated.</sub>

[⬅ Back to the repository](../README.md) · [AI Engineering](../ai-engineering-by-RDJ/README.md) · [Python Lab](../python-by-RDJ/README.md)

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](./LICENSE).

</div>
