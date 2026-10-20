# Glossary

This glossary defines the terms that the Nexgen Server documents use.

## Project terms

| Term | Definition |
|---|---|
| **Actuator** | A versioned, named Python method that processes data in a SemCom pipeline. Nexgen Server stores its source code and its package requirements. |
| **Coding actuator** | An actuator with `actuator_type: coding`. It changes a source into a representation for transmission. |
| **Decoding actuator** | An actuator with `actuator_type: decoding`. It changes a received representation into a reconstruction or a task decision. |
| **Latest version** | The one active version of an actuator name with `latest: true`. Clients use it, and new data items must come from it. |
| **Data item** | The output of an actuator, with a reference to that actuator. |
| **Content item** | The original version of the data. |
| **Linked resource** | The field of a data item that refers to the original input, for example a content `identifier`. |
| **Specs** | Free-form key–value information on a data item or a content item. |
| **Soft delete** | A delete operation that sets `active: false` and keeps the document. |

## SemCom terms

| Term | Definition |
|---|---|
| **Semantic communication (SemCom)** | A communication paradigm whose design objective is the correct delivery of the meaning, or of the task-relevant content, of a message. |
| **Goal-oriented / task-oriented communication** | SemCom in which the receiver must perform a task (classification, detection, control), not reconstruct the source. The transmitter transmits only task-relevant features. |
| **Semantic information** | The meaning that a message carries relative to a shared context or shared knowledge. It is different from Shannon's statistical (syntactic) information. The field has no agreed definition or unit yet. |
| **Semantic encoder** | A module (usually a neural network) that extracts a compact representation of the meaning, or of the task-relevant features, of the source. |
| **Semantic decoder** | A module that interprets the received representation. It recovers the meaning, reconstructs the source, or outputs a task decision directly. |
| **Channel encoder / decoder** | A module that protects semantic features against channel impairments. In learned systems, it is often merged with the semantic encoder (see JSCC). |
| **Knowledge base (KB)** | Shared background knowledge that the transmitter and the receiver use to encode and interpret meaning. Examples: datasets, trained model weights, ontologies, knowledge graphs, codebooks. |
| **Background knowledge mismatch** | A divergence between the KB of the transmitter and the KB of the receiver. It causes misinterpretation even when the physical link has no errors. |
| **Semantic noise** | Any disturbance that changes meaning. Examples: ambiguity, KB mismatch, physical-channel errors that change semantics, adversarial perturbations. |
| **Semantic fidelity** | The degree to which the received meaning matches the transmitted meaning. |
| **Joint source–channel coding (JSCC)** | Coding that designs compression and error protection together. It replaces the separate chain of source coding and channel coding. |
| **Deep JSCC (DJSCC)** | JSCC in which the encoder and the decoder are neural networks, trained end-to-end through a differentiable channel model. |
| **Separate source–channel coding (SSCC)** | The conventional design, for example JPEG/BPG/VVC + LDPC/Polar codes. It is optimal only asymptotically (infinite block length). |
| **Cliff effect** | In digital SSCC, the reconstruction quality collapses abruptly when the channel SNR drops below the design point. |
| **Graceful degradation** | The quality decreases smoothly as the SNR decreases. This is a hallmark of DJSCC. |
| **Channel bandwidth ratio (CBR)** | The ratio of channel uses *k* to source dimension *n* (for example, pixels). It is the "compression rate" of a JSCC scheme. |
| **Signal-to-noise ratio (SNR)** | `SNR = 10·log10(P/σ²)`, in dB |
| **Digital SemCom** | The system quantizes latent features and maps them to standard constellations (BPSK, QAM). This gives compatibility with existing systems. |
| **Vector quantization (VQ) / codebook** | The system maps each continuous feature vector to the nearest entry of a learned codebook and transmits the index. |
| **Generative SemCom (GenSC)** | SemCom in which the receiver regenerates content from compact semantic cues with a generative prior (VAE, GAN, diffusion model, LLM). |
| **Hallucination** | Generated content that looks correct but is wrong |
| **Token communication (TokenCom)** | A recent paradigm that uses the tokens of large (multimodal) models as the unit of communication. |
| **Age of Information (AoI)** | The time since the generation of the latest received update. It measures freshness. |
| **VoI / UoI / AoII** | Value of Information, Urgency of Information, Age of Incorrect Information. These are goal-oriented extensions of AoI. |

## Notation

| Symbol | Meaning |
|---|---|
| `s` | Source message (sentence, image, signal) |
| `z` | Semantic latent / feature vector |
| `x` | Channel input symbols |
| `y` | Channel output, `y = h·x + n` |
| `h` | Channel coefficient / matrix (CSI) |
| `n ~ CN(0, σ²)` | Additive white Gaussian noise |
| `ŝ` | Reconstructed source or task output |
| `k / n` | Channel bandwidth ratio (CBR) |
| `K_T`, `K_R` | Transmitter / receiver knowledge base |
