# What Is Semantic Communication?

**Semantic communication (SemCom)** is a communication paradigm. Its design objective is the correct delivery of the *meaning* (or the *task-relevant content*) of a message. Its objective is not the bit-exact reproduction of the transmitted symbols.

Classical (Shannon) systems treat the link as a pipe that ignores content. They measure success with the bit error rate (BER) or the block error rate. SemCom changes the objective from **symbol fidelity** to **semantic fidelity**. In its goal-oriented form, the objective is **task success**.

## Weaver's three levels of communication

The literature usually frames the field with Warren Weaver's extension of Shannon's theory (1949).

| Level | Problem | Question asked | Typical metric |
|---|---|---|---|
| **A — Technical** | Syntactic | How accurately can the symbols be transmitted? | BER, BLER, PSNR |
| **B — Semantic** | Meaning | How precisely do the symbols convey the intended meaning? | Sentence similarity, LPIPS, semantic distortion |
| **C — Effectiveness** | Pragmatic / goal | How effectively does the received meaning affect behaviour / achieve the goal? | Task accuracy, control cost, AoI/VoI |

Level B is "semantic communication" in the narrow sense. Level C is **goal-oriented** (also called **task-oriented** or **effectiveness-level**) communication. Most current literature puts both levels under the SemCom name.

## Why it matters

- **Efficiency:** A system that sends only the semantically relevant information needs less bandwidth and power, and has lower latency.
- **Robustness:** Learned joint source–channel schemes lose quality gradually at low SNR. They do not fail abruptly.
- **AI-native networks:** 6G is expected to carry machine-to-machine and agent-to-agent traffic. In that traffic, the receiver is a model that executes a task, not a human who views raw data.
