# Key Technical Concepts

## 1. Deep Joint Source–Channel Coding (DJSCC)

- The encoder maps source samples *directly* to complex channel symbols. The encoder and the decoder are trained jointly as an **autoencoder with a non-trainable noisy channel layer** in the middle.
- Seminal result (Bourtsoulatze, Kurka, Gündüz, 2019):
  - DJSCC outperformed JPEG/JPEG2000 + capacity-achieving channel codes at low SNR and low bandwidth.
  - It showed **no cliff effect**.
  - On slow Rayleigh fading, it learned robust representations even **without explicit pilots or channel estimation**.
- **Training:** The channel (AWGN, fading) is simulated inside the computational graph. The loss is typically MSE, MS-SSIM, LPIPS or a task loss. A normalization layer enforces the average power constraint.
- **SNR-adaptive models** receive the channel SNR (or CSI) as side information (for example, through attention modules). Thus one model serves many channel conditions.

## 2. Transformer-based semantic coding (DeepSC)

- **DeepSC** (Xie, Qin, Li, Juang, 2021) is a text SemCom system. It has a Transformer semantic encoder and decoder, and a dense-layer channel encoder and decoder.
- The training loss combines cross-entropy (semantic error) with a mutual-information term that maximizes channel throughput:

  `L_total = L_CE(s, ŝ) − λ · I(x; y)`

- DeepSC introduced the **sentence similarity** metric (cosine similarity of BERT embeddings). It used **transfer learning** to adapt to new knowledge domains and channels.
- Its most robust gains appear at **low SNR**. It received the 2023 IEEE SPS Best Paper Award.
- It started a family of systems: DeepSC-S (speech), DeepSC-ST (speech-to-text), MU-DeepSC (multi-user/multimodal), L-DeepSC (lite/IoT).

## 3. Content-adaptive coding: NTSCC and SwinJSCC

- **NTSCC (Nonlinear Transform Source–Channel Coding):**
  - A nonlinear analysis transform maps the source to a latent *y*.
  - A learned **entropy model (hyperprior)** estimates the information content of each latent element. This estimate drives **variable-length / adaptive-rate** JSCC.
  - Improved NTSCC reported channel bandwidth savings versus a VTM + 5G LDPC baseline.
- **SwinJSCC:**
  - It has a Swin-Transformer backbone, *Channel ModNet* (channel-state awareness) and *Rate ModNet* (rate control).
  - Thus one model adapts to both the SNR and the target rate.
  - Open source: <https://github.com/semcomm/SwinJSCC>.
- General principle: **semantic importance-aware rate allocation**. Spend more channel uses on the content that matters.

## 4. Digital semantic communication

Real networks are digital. Analog DJSCC outputs (arbitrary constellation points) are hard to deploy on existing RF chains and protocols.

| Approach | Mechanism | Trade-off |
|---|---|---|
| **Scalar quantization (SQ-JSCC)** | Each feature element is quantized to learned levels or constellation points. | Simple. Has quantization loss. |
| **Vector quantization (VQ-JSCC)** | Each feature vector is mapped to the nearest codebook vector (VQ-VAE style). The index is transmitted through BPSK/QAM. | Compact. The codebook size is often tied to the modulation order. |
| **Residual VQ / multilevel codebooks** | Recursive quantization of residuals (for example, MOC-RVQ). | Better fidelity at a low channel bandwidth ratio. |
| **Channel-aware VQ** | Codebook training uses the channel transition probabilities. Thus symbols that are easily confused map to semantically similar codewords (for example, VQJSCC). | Mitigates the *digital* cliff effect. |
| **Bit-level / hybrid JSCC–SSCC** | Semantic bits go through standard channel codes. This decouples the quantization level from the modulation order. | Highest compatibility. Loses some joint gains. |

The quantizer is not differentiable. To train through it, systems typically use **straight-through estimators** or **Gumbel-Softmax** relaxation.

## 5. Knowledge bases and background-knowledge mismatch

- The KB is the source of the "subjectivity" of meaning. The encoder and the decoder must share compatible knowledge. They typically get it from training on common data.
- **Mismatch** occurs in these cases:
  - The KBs evolve independently.
  - The KBs cannot be shared, for privacy or overhead reasons.
  - The devices belong to different domains.
- Mitigations:
  - Periodic parameter sharing, or **federated or cooperative training** of encoder–decoder pairs.
  - **KB identification** (estimate the degree of match before transmission).
  - Lightweight **adapter layers**.
  - KB-aware model selection at base stations.
- Recent work uses **knowledge graphs** and **retrieval-augmented generation (RAG)** as explicit KBs that can be updated.

## 6. Goal-oriented communication and information freshness

- The **value of the update to the goal** drives each transmission decision, not the data volume.
- **AoI** measures freshness. The variants **VoI, UoI, AoII** add relevance, urgency and correctness. The **Goal-oriented Tensor (GoT)** has been proposed to unify them.
- Typical analysis tools: **Markov decision processes (MDPs)**, **Lyapunov optimization**, remote estimation of Markov sources.
- Typical decisions: *when* to sample, *what* to transmit, *whom* to schedule.
- Applications: networked control, cooperative perception for vehicles, industrial IoT, UAV swarms.

## 7. Generative semantic communication

- The receiver uses a learned generative prior to **regenerate** content from minimal cues. This is a shift from *information recovery* to *information regeneration*.
- Model families:
  - **VAE:** probabilistic latents. A natural fit for JSCC.
  - **GAN:** reconstruction with perceptual quality at extreme compression.
  - **Diffusion models (DMs):** currently the most active family. They have three uses:
    1. Generative decoders, conditioned on received latents, text or edges.
    2. **Channel denoisers** (for example, CDDM — Channel Denoising Diffusion Models).
    3. Posterior-sampling receivers that treat semantic decoding as inverse-problem inference.

    Key enabling techniques: conditional diffusion, accelerated or few-step sampling, latent diffusion.
  - **LLMs / multimodal LLMs:** semantic encoders and decoders, compressors, KBs, or receivers. They serve text, image (through captioning + text-to-image) and multimodal sources.
- **Caveat:** Generated content can be *perceptually plausible but factually wrong* (hallucination). Metrics must check semantic consistency, not only perceptual quality.

## 8. Large-model-driven SemCom

- **LLM-SC:** LLMs applied directly to the physical-layer coding and decoding of text. They model the transmitted sequences probabilistically.
- **LLM encoders + OFDM** pipelines for image transmission.
- **Prompt-based / language-oriented SemCom:** the messages are natural language or compact prompts.
- **Large AI Models (LAMs)** as shared KBs at both ends. This reduces the need to transmit what both sides already "know".
- Deployment pressure: the model size is in conflict with the device constraints. Responses: **split inference**, **tiny language models**, **mixture-of-experts over wireless**, edge–cloud collaboration.

## 9. Token communication (TokenCom), emerging (2025–2026)

- **Motivation:** Semantic representations are tied to specific modalities and models. **Tokens** from unified multimodal models give a common unit across text, image, audio, video and robot actions.
- **Ideas:**
  - Token-level **importance assignment**.
  - **Unequal error protection**. For example, TokCom-UEP uses the fact that 1D token sequences have decreasing semantic importance from head to tail.
  - **Cross-modal context** for token prediction and correction at the receiver.
  - **Semantic packet aggregation**.
- **Agentic communication:** chain-of-agents frameworks plan and adapt the token pipeline (Agentic TokenCom, IEEE TCCN 2026).
- **Related:** **direct model-to-model semantic exchange**. For example, Cache-to-Cache (C2C) passes a projected KV-cache between LLMs instead of generated text.

## 10. Multi-user, network and system-level topics

- **Multiple access:** semantic feature division multiple access (SFDMA), model-division multiple access (MDMA), NOMA for semantic streams.
- **Resource allocation:** semantic-aware spectrum and power allocation, user association by KB match, semantic spectral efficiency.
- **HARQ and transport:** semantic HARQ (incremental redundancy on features), semantic transport protocols that avoid retransmission.
- **Semantic RAN (SemRAN):** semantic functions embedded in the RAN architecture.
- **Integration with:** ISAC, RIS / stacked intelligent metasurfaces, NTN/satellite, MIMO precoding, edge computing, digital twins.
