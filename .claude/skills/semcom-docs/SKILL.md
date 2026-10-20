---
name: semcom-docs
description: Terminology, theory, techniques, metrics, state of the art (2019 to 2026), standardization status and writing conventions for semantic communication (SemCom). Use when you write, review or explain a README, docs, docstrings, API descriptions, comments or reports for this project. Topics: semantic communication, goal-oriented or task-oriented communication, JSCC, deep JSCC, DeepSC, NTSCC, SwinJSCC, knowledge bases, semantic encoders and decoders. More topics: generative or token communication, 6G, IMT-2030, and the coding and decoding actuators of this project. Also use when the user asks what a SemCom term means.
---

# Semantic Communication Docs

Use this skill to write accurate documentation for this semantic communication (SemCom) project. The facts are in the files in `references/`. Write the text with the `asd-ste100` skill.

## 1. Accuracy rules

1. Use only the facts in `references/`. Do not add a number, a date, an author, a result or an award from memory.
2. If a document needs a fact that is not in `references/`, tell the user. Ask for a source, or write `TODO: source needed` in the text.
3. Cite only the items in `references/bibliography.md`. Copy each title, DOI, arXiv ID and URL exactly. Do not invent a citation.
4. Mark each arXiv item without peer review with *(preprint)*. `references/bibliography.md` shows which items are preprints.
5. Keep the strength of each claim. Keep words such as "is expected", "often", "typically", "reported" and "has been proposed". Do not change a proposal into a standard. Do not change "reported bandwidth savings" into a number.
6. Put a date on each statement about standardization. Example: "as of 3GPP Rel-20, Oct 2026".
7. Do not write that a 3GPP release or an ITU recommendation specifies SemCom. As of October 2026, no 3GPP release specifies SemCom.
8. Do not write that semantic information has an agreed definition or an agreed unit. The field does not have one yet.
9. Keep the two objectives separate. In semantic-level communication, the receiver recovers the meaning. In goal-oriented (task-oriented) communication, the receiver does a task.
10. If a document describes a generative receiver, say that it can make content that looks correct but is wrong (hallucination). Name a metric that checks semantic consistency.

The facts in `references/` come from the user's document "Semantic Communication — Terminology, State of the Art & Technical Concepts", compiled in October 2026. This skill does not check those facts against the primary sources. Before a document is published, tell the user to check each number, date and award against the cited paper.

## 2. Reference files

Read only the files that the task needs.

| File | Contents | Read it when the document… |
|---|---|---|
| `references/overview.md` | Definition of SemCom, Weaver's three levels, why SemCom matters | introduces the project or the field |
| `references/glossary.md` | Definitions of the core terms and abbreviations | uses any SemCom term |
| `references/theory.md` | Semantic information theory, rate–distortion, information bottleneck, open theory problems | makes a theoretical claim |
| `references/architecture.md` | Reference pipeline (Mermaid diagram) and its variants | describes the system architecture or data flow |
| `references/techniques.md` | DJSCC, DeepSC, NTSCC, SwinJSCC, digital SemCom, knowledge bases, goal-oriented, generative, large-model and token communication, multi-user topics | explains a method or names a related system |
| `references/metrics.md` | Metrics for each modality, and the reporting practice | reports results or describes an evaluation |
| `references/state-of-the-art.md` | Timeline 1949 to 2026, research directions, surveys, open challenges | writes a background, related-work or roadmap section |
| `references/standardization.md` | ITU-R, IMT-2030 Promotion Group, 3GPP, CCSA, ETSI, IEEE | mentions 6G, 3GPP or standards |
| `references/security.md` | Threats and countermeasures | writes a security or privacy section |
| `references/bibliography.md` | All citations, grouped by topic | cites a source |
| `templates/readme-outline.md` | Section outline for a SemCom project README | writes or restructures the README |

## 3. Project context

This repository (Nexgen Server) stores *actuators*. An actuator is a versioned, named Python method. Its `actuator_type` is `coding` or `decoding`.

The code does not say which SemCom block an actuator implements. A `coding` actuator can be a semantic encoder, a channel encoder or a joint (JSCC) encoder. Before a document connects an actuator type to a SemCom block, ask the user which connection to use. Then use that connection in all documents.

## 4. Process

1. Identify the document type and the reader. Examples: a README for new contributors, an API reference for client developers, a design note for researchers.
2. Read the reference files for the topics of the document (see section 2).
3. Write the draft. Use each term from `references/glossary.md` with one meaning in all documents.
4. Apply the `asd-ste100` skill:
   - Use STE-flavored mode for READMEs, design notes and explanatory text.
   - Use Strict mode for procedures, error messages, endpoint descriptions and tool descriptions.
5. From the repository root, run the STE linter on the file: `python3 .claude/skills/asd-ste100/scripts/ste-lint.py <file>`. Remove the hard violations.
6. Do the checks in section 6.

## 5. Writing conventions

### Names

- At the first use in a document, write "semantic communication (SemCom)". After that, write "SemCom".
- Write "joint source–channel coding (JSCC)", "deep JSCC (DJSCC)" and "separate source–channel coding (SSCC)".
- Define each abbreviation at its first use in each document. Take the definition from `references/glossary.md`.
- Use one name for one thing. For example, do not change between "semantic encoder", "semantic coder" and "feature extractor" for one module.

### Notation

Use these symbols in all documents.

| Symbol | Meaning |
|---|---|
| `s` / `x_src` | Source message (sentence, image, signal) |
| `z` | Semantic latent / feature vector |
| `x` | Channel input symbols (complex, power-normalized) |
| `y` | Channel output, `y = h·x + n` |
| `h` | Channel coefficient / matrix (CSI) |
| `n ~ CN(0, σ²)` | Additive white Gaussian noise |
| `ŝ` | Reconstructed source or task output |
| `k / n` | Channel bandwidth ratio (CBR) |
| `SNR = 10·log10(P/σ²)` | Signal-to-noise ratio in dB |
| `K_T`, `K_R` | Transmitter / receiver knowledge base |

### Results and experiments

For each result, state these six items:

1. Source modality
2. Channel model
3. SNR range for training and for test
4. CBR
5. Metric
6. Baseline

Show performance as a function of SNR and as a function of CBR. Say if the training SNR and the test SNR are different. Compare with a strong SSCC baseline, for example BPG/VVC + LDPC/Polar with adaptive MCS. See `references/metrics.md`.

### Claims

- Do not write "robust", "efficient" or "better" without the condition and the measurement that support the claim.
- Do not write marketing words such as "revolutionary", "seamless" or "cutting-edge".

## 6. Checks before you finish

- [ ] Each fact comes from `references/` or from a source that the user gave.
- [ ] Each citation is in `references/bibliography.md`, and its identifiers are exact.
- [ ] Each preprint has the *(preprint)* mark.
- [ ] Each standardization statement has a release or a date.
- [ ] Each hedge from the reference is still in the text.
- [ ] Each abbreviation is defined at its first use.
- [ ] The document says whether the objective is semantic-level or goal-oriented.
- [ ] Each result states the six items in section 5.
- [ ] The STE linter shows no hard violations, or the user accepted the remaining ones.
