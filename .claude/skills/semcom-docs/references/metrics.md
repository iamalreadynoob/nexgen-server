# Evaluation Metrics

| Category | Metric | Notes |
|---|---|---|
| **Text** | BLEU (n-gram) | Lexical. Misses synonyms and paraphrase. |
| | Sentence similarity (BERT / SBERT cosine) | Introduced by DeepSC. Matches meaning through embeddings. |
| | WER / CER | For speech-to-text pipelines. |
| | BERTScore, METEOR, LLM-as-judge | Used more and more for generative systems. |
| **Image / video** | PSNR, MSE | Pixel level (close to Level A). |
| | SSIM, MS-SSIM | Structural fidelity. |
| | LPIPS, DISTS | Learned perceptual similarity. |
| | FID, KID | Realism at the distribution level (generative receivers). |
| | CLIP score / semantic segmentation mIoU | Semantic consistency of reconstructions. |
| **Speech** | PESQ, STOI, SDR | Perceptual quality and intelligibility. |
| **Task-oriented** | Classification accuracy, detection mAP, retrieval recall | Measured on the received features or on the reconstructions. |
| **Goal / timing** | AoI, VoI, AoII, control cost, task completion latency | Effectiveness level. |
| **System** | CBR, semantic spectral efficiency, energy per task, model size / FLOPs, inference latency | Necessary for a fair comparison and for deployability. |

## Good practice for papers and docs

- Report performance as curves against **SNR** and against **CBR**.
- Specify the channel model.
- Say whether the SNR is mismatched between training and testing.
- Compare against a strong SSCC baseline, for example BPG/VVC + LDPC/Polar with adaptive MCS.
- For generative receivers, also check semantic consistency, not only perceptual quality (see `techniques.md`, section 7).
