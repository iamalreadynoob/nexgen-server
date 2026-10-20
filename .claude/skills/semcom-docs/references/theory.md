# Theoretical Foundations

## Classical semantic information theory

- **Carnap & Bar-Hillel (1952)** proposed the first quantitative theory of semantic information. They did not use statistical frequency. They measured the information in a sentence with the *logical probability* that the sentence is true across possible worlds. A sentence that rules out more states of the world carries more information.
- **Bar-Hillel–Carnap paradox:** Under this measure, a contradiction gets the *maximum* information. This result is counter-intuitive.
- **Floridi — Theory of Strongly Semantic Information:** It adds a truthfulness requirement to resolve the paradox. **D'Alfonso** proposed measures based on *truthlikeness*.
- **Bao et al. (2011)** built a semantic communication model that mirrors Shannon's framework. It defines semantic entropy and semantic source and channel coding theorems. But it is restricted to propositional logic.

## Modern information-theoretic tools

| Tool | Role in SemCom |
|---|---|
| **Rate–distortion theory** | Generalized with semantic or perceptual distortion measures. For generative receivers, there is a *rate–distortion–perception* trade-off. |
| **Information bottleneck** | Formalizes "keep only what is relevant to the task." |
| **JSCC theory** | Finite block-length analysis shows where separation is suboptimal. DJSCC gains appear in that regime. |
| **Side-information coding (Slepian–Wolf, Wyner–Ziv)** | Models the knowledge base of the receiver as side information at the decoder. |
| **Semantic capacity / semantic channel capacity** | The upper limit of semantic information that one channel use can transfer. It is still an open research problem. |

## Status

The field still has no universally accepted mathematical definition of semantic information. It also has no unified representation unit comparable to the bit. Papers repeatedly cite this as a fundamental open problem.
