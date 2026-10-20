# Security

This document describes the security of the API, the risks of stored actuator code, and the threats that apply to semantic communication (SemCom) systems.

## API authentication

- The server checks the `X-API-Key` header on all endpoints except health. The check uses a constant-time comparison.
- If `API_KEY` is empty or not set, authentication is off. The server logs a warning at startup.
- The server has one access level. Each valid key can read, create, change and delete all items.

See [Configuration](configuration.md#authentication).

Recommendations:

1. Always set `API_KEY` outside of local development.
2. Give each client its own key. Then you can revoke one key without an effect on the other clients.
3. Put the server behind a TLS proxy. The server itself does not use TLS, so clients send the API key in plain text.
4. Set `ENVIRONMENT=production` to turn off the `/docs` page.

## Stored actuator code

An actuator contains Python source code in `method` and a list of packages in `requirements`. The server does not run this code. The clients that get an actuator run it.

> [!WARNING]
> Each client that runs an actuator runs code that another API user wrote. A user with a valid key can store code that does harm on each client that runs it.

Recommendations for clients:

1. Run actuator code in an isolated environment, for example a container or a sandbox with no access to secrets.
2. Install `requirements` in a separate virtual environment. Do not install them in the environment of the client application.
3. Pin package versions in `requirements`, for example `numpy==2.1.0`.
4. Give API keys only to users that you trust to write actuator code.

## SemCom threats

SemCom systems have threats that link-level metrics often do not show.

| Threat | Description | Where it applies to Nexgen Server |
|---|---|---|
| **Semantic eavesdropping / inference** | Intercepted features can show content or private attributes. An attacker can invert features to reconstruct recognizable images. | Data items store actuator outputs, for example embeddings. Protect them like the original content. |
| **Adversarial perturbations** | Small crafted perturbations cause large semantic errors. | Inputs to coding actuators, and data on the link |
| **Semantic manipulation / latent tampering** | An attacker changes the meaning while the link appears healthy. | A user with a valid key can change `linked_resource` and `specs` of data items. |
| **Model-level attacks** | Data poisoning, backdoors, model extraction, model inversion | Actuators that load models, and content that is used for training |
| **Availability attacks** | Jamming, flooding, and denial of service (DoS) that uses all the computation of semantic processing | The API and the clients that run actuators |
| **Knowledge base (KB) attacks** | Corruption or desynchronization of shared knowledge bases | The latest flag of an actuator. A change of the latest version changes the actuator that all clients use. |

Countermeasures from the literature:

- Adversarial training
- Input transformation and detection
- Differential privacy
- Semantic encryption and key generation
- Physical-layer security (artificial noise, covert transmission)
- Federated learning
- Blockchain-based KB integrity
- Learning methods that resist poisoning

For surveys of secure SemCom, see [References](references.md#security).
