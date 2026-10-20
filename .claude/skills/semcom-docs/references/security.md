# Security and Privacy

| Threat | Description |
|---|---|
| **Semantic eavesdropping / inference** | Intercepted features can reveal content or private attributes. An attacker can invert features to reconstruct recognizable images. |
| **Adversarial perturbations** | Small crafted perturbations (on the input or over the air) cause large semantic errors. Link-level metrics often do not show these errors. |
| **Semantic manipulation / latent tampering** | An attacker changes the meaning while the link appears healthy. |
| **Model-level attacks** | Data poisoning, backdoors, model extraction, model inversion. |
| **Availability attacks** | Jamming, flooding, and DoS that exhausts the computation of semantic processing. |
| **KB attacks** | Corruption or desynchronization of shared knowledge bases. |

## Countermeasures

- Adversarial training
- Input transformation and detection
- Differential privacy
- Semantic encryption and key generation
- Physical-layer security (artificial noise, covert transmission)
- Federated learning
- Blockchain-based KB integrity
- Robust learning against poisoning
