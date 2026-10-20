# State of the Art (2019 to 2026)

## Timeline of milestones

| Year | Milestone | Significance |
|---|---|---|
| 1949–1952 | Weaver's three levels. Carnap & Bar-Hillel semantic information. | Conceptual and theoretical origins. |
| 2018 | DeepNN / LSTM-based JSCC for text (Farsad et al.) | First deep text JSCC (word-error metric). |
| 2019 | **Deep JSCC** for wireless images | Graceful degradation, no cliff effect. |
| 2021 | **DeepSC** (Transformer text SemCom) | Sentence similarity metric. Benchmark system. |
| 2021–2022 | DeepSC-S, MU-DeepSC, task-oriented edge inference, information-bottleneck designs | Expansion to multimodal and task-oriented SemCom. |
| 2022 | **NTSCC** | Adaptive-rate JSCC guided by an entropy model. |
| 2023 | **SwinJSCC**, improved NTSCC, digital VQ-based SemCom | Versatile models that are easier to deploy. Digital compatibility. |
| 2023–2024 | Diffusion-based receivers (for example, CDDM), GAN/VAE generative SemCom | Rise of **generative SemCom**. |
| 2024 | LLM-SC. Major surveys (Proc. IEEE, IEEE Access). | Start of the large-model era. |
| 2025 | Generative SemCom architectures with LLM-native agents. **Token communications** proposed. Surveys of secure SemCom. | Attempts at unification. |
| 2026 | Agentic TokenCom. TokenCom positioned as the evolution of SemCom. SemRAN architectures. Benchmarks (6G-Bench). | SemCom at the network level and the agent level. |

## Main research directions today

1. **Generative / diffusion-based SemCom:** extreme compression with perceptual quality. The focus is on fast sampling and hallucination control.
2. **Large-model-driven SemCom and TokenCom:** foundation models as shared knowledge. Tokens as the unit of communication.
3. **Digital and standard-compatible SemCom:** quantization, codebooks, constellation mapping, coexistence of semantic traffic and bit traffic.
4. **Goal-oriented and agent-oriented communication:** AoI/VoI scheduling, agent-to-agent protocols, multi-agent coordination.
5. **Robustness, security and trust:** adversarial robustness, semantic privacy, KB mismatch.
6. **Theory:** semantic entropy, semantic capacity, rate–distortion–perception.

## Representative surveys (start here)

Full citations are in `bibliography.md`.

- Getu, Kaddoum, Bennis — *Semantic Communication: A Survey on Research Landscape, Challenges, and Future Directions*, Proc. IEEE (2024/2025).
- Getu, Kaddoum, Bennis — *A Survey on Goal-Oriented Semantic Communication*, IEEE Access (2024).
- Getu, Kaddoum, Bennis — *Making Sense of Meaning: A Survey on Metrics for Semantic and Goal-Oriented Communication*, IEEE Access (2023).
- Lu et al. — *Semantics-Empowered Communication: A Tutorial-cum-Survey*.
- Gündüz et al. — *Beyond Transmitting Bits: Context, Semantics, and Task-Oriented Communications*, IEEE JSAC.
- Zhou et al. — *Generative Semantic Communication: Architectures, Technologies, and Applications*, Engineering (2025).
- Qin et al. — *Generative AI Meets 6G and Beyond: Diffusion Models for Semantic Communications* (2025, preprint).
- *From Semantic to Token Communication* (2026, preprint).

## Open challenges

1. **Theory:** There is no agreed definition or measure of semantic information, semantic capacity or a "semantic bit".
2. **Generalization:** Models trained on one dataset, modality or channel degrade on others. The field needs approaches at foundation-model scale or with continual learning.
3. **KB management:** synchronization, versioning, privacy-preserving sharing, mismatch detection.
4. **Digital compatibility and coexistence** with legacy bit pipes, protocol stacks and HARQ.
5. **Complexity and energy:** large encoders and decoders on constrained devices. Inference latency of diffusion models and LLMs.
6. **Evaluation:** There are no standard benchmarks and KPIs. Perceptual metrics do not show semantic correctness. Generative receivers can hallucinate.
7. **Trust and security:** integrity verification and explainability at the semantic level.
8. **Multi-user and network scale:** semantic-aware scheduling, multiple access, routing and caching.
9. **Standardization:** interoperable interfaces between the learned encoders and decoders of different vendors.
