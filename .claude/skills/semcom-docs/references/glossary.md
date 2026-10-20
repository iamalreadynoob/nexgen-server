# Glossary of Core Terminology

Use each term with the meaning in this table. `techniques.md` explains more terms in context (for example SFDMA, MDMA, CDDM, SemRAN and split inference).

| Term | Definition |
|---|---|
| **SemCom** | Common abbreviation for semantic communication. |
| **Goal-oriented / task-oriented communication** | SemCom in which the receiver must perform a task (classification, detection, control), not reconstruct the source. The transmitter transmits only task-relevant features. |
| **Semantic information** | The meaning that a message carries relative to a shared context or shared knowledge. It is different from Shannon's statistical (syntactic) information. |
| **Semantic encoder** | A module (usually a neural network) that extracts a compact representation of the meaning, or of the task-relevant features, of the source. |
| **Semantic decoder** | A module that interprets the received representation. It recovers the meaning, reconstructs the source, or outputs a task decision directly. |
| **Channel encoder / decoder** | A module that protects semantic features against channel impairments. In learned systems, it is often merged with the semantic encoder (see JSCC). |
| **Knowledge base (KB)** | Shared background knowledge that the transmitter and the receiver use to encode and interpret meaning. Examples: datasets, trained model weights, ontologies, knowledge graphs, codebooks. |
| **Background knowledge mismatch** | A divergence between the KB of the transmitter and the KB of the receiver. It causes misinterpretation even when the physical link has no errors. |
| **Semantic noise** | Any disturbance that changes meaning. Examples: ambiguity, KB mismatch, physical-channel errors that change semantics, adversarial perturbations. |
| **Semantic entropy** | A measure of the semantic uncertainty of a message. The classical definition (Carnap & Bar-Hillel) uses *logical* probability, not statistical probability. |
| **Semantic fidelity** | The degree to which the received meaning matches the transmitted meaning. |
| **JSCC (Joint Source–Channel Coding)** | Coding that designs compression and error protection together. It replaces the separate chain of source coding and channel coding. |
| **Deep JSCC (DJSCC)** | JSCC in which the encoder and the decoder are neural networks, trained end-to-end through a differentiable channel model. |
| **SSCC (Separate Source–Channel Coding)** | The conventional design, for example JPEG/BPG/VVC + LDPC/Polar codes. It is optimal only asymptotically (infinite block length). |
| **Cliff effect** | In digital SSCC, the reconstruction quality collapses abruptly when the channel SNR drops below the design point. Above that point, the quality does not improve further (leveling-off). |
| **Graceful degradation** | The quality decreases smoothly as the SNR decreases. This is a hallmark of DJSCC. |
| **CBR (Channel Bandwidth Ratio)** | The ratio of channel uses *k* to source dimension *n* (for example, pixels). It is the "compression rate" of a JSCC scheme. |
| **Analog SemCom** | The system maps continuous-valued latent features directly to channel symbols, with no quantization. |
| **Digital SemCom** | The system quantizes latent features (scalar or vector quantization) and maps them to standard constellations (BPSK, QAM). This gives compatibility with existing systems. |
| **Vector quantization (VQ) / codebook** | The system maps each continuous feature vector to the nearest entry of a learned codebook and transmits the index. This is the basis of VQ-VAE-style digital SemCom. |
| **Generative SemCom (GenSC)** | SemCom in which the receiver *regenerates* content from compact semantic cues with a generative prior (VAE, GAN, diffusion model, LLM). |
| **Token communication (TokenCom / TokCom)** | A recent paradigm that uses the tokens of large (multimodal) models as the unit of communication. It enables token-level importance, error handling and resource allocation. |
| **Semantic importance / UEP** | The system gives different protection (unequal error protection) or a different rate to features according to their semantic importance. |
| **AoI (Age of Information)** | The time since the generation of the latest received update. It measures freshness. |
| **VoI / UoI / AoII** | Value of Information, Urgency of Information, Age of Incorrect Information. These are goal-oriented extensions of AoI. |
| **Information bottleneck (IB)** | A principle: compress input *X* into a representation *Z* that keeps maximal information about target *Y* and discards the rest. It is a theoretical lens for task-oriented coding. |
| **Semantic rate–distortion** | Rate–distortion theory that measures distortion in semantic (or task) space, not in signal space. |
| **ISAC** | Integrated Sensing and Communication. 6G research frequently combines it with task-oriented SemCom. |
| **IMT-2030** | The formal ITU designation for 6G. |
| **Intellicise** | A term ("intelligent + concise") that Chinese 6G research uses for semantic-native network design. |
