# PRISMA™ — Platform for Reflection and Interpretation in Multidimensional Assessment of Learning

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Edge AI](https://img.shields.io/badge/Inference-100%25_Offline-purple.svg)]()
[![Child Data Sovereignty](https://img.shields.io/badge/Child_Data-Air--Gapped-red.svg)]()

PRISMA™ is an open-source, air-gapped, edge-AI qualitative pedagogical transducer. It is designed to bridge international competency frameworks with community-based learning models. The system analyzes, synthesizes, and maps brief teacher notes, projecting their significance for individual learners’ transformation/growth onto an eight-dimensional vector space (R^8).
Developed as the analytical intero-proprioceptive engine of the **ASPIRE® Ecosystem** (INDAUTOR Reg. 03-2026-040710022300-01 | SSRN DOI: [10.2139/ssrn.7310080](https://doi.org/10.2139/ssrn.7310080)).

---

## 🌟 Core Architectural Principles

1. **Human-Always-in-Charge:** PRISMA only suggests transformation hypotheses based on factual pedagogical observations. The educator maintains inalienable authority to accept, adjust, or reject deltas.
2. **100% Offline / Air-Gapped Sovereignty:** Operates strictly on local hardware with zero external API calls, eliminating cloud telemetry, recurring SaaS token costs, and child privacy risks by design.
3. **Biopsychosocial Safeguards:** Features a non-punitive "State of Educability" baseline (sleep, nutrition, somatic distress/dysmenorrhea/care burdens) to systematically dampen punitive misdiagnosis and recognize resilience under fatigue.
4. **Logarithmic R^8 Vector Space:** Maps multidimensional growth using Weber-Fechner decibel scaling (ΔdB = 20 · log10(1 + g), where +6 dB represents a calibrated 2x doubling of capability relative to baseline) across 8 complementary axes.

---

## 📐 R^8 Developmental Vector Axes

* **Inquiry & Research** (*Indagación e investigación*)
* **Critical & Analytical Thinking** (*Pensamiento crítico y analítico*)
* **Ethical Reasoning** (*Razonamiento ético*)
* **Intercultural Agency** (*Agencia intercultural*)
* **Collaborative Leadership** (*Liderazgo colaborativo*)
* **Practical & Technical Mastery** (*Saber hacer y ejecución técnica*)
* **Resilience & Self-Management** (*Resiliencia y autogestión*)
* **Metacognitive Reflection** (*Reflexión metacognitiva*)

---

## 🚀 Quickstart & Local Installation

### Prerequisites
* Python 3.10 or higher
* [Ollama](https://ollama.ai/) installed and running locally

### 1. Clone Repository
```bash
git clone [https://github.com/vicstern/PRISMA_App.git](https://github.com/vicstern/PRISMA_App.git)
cd PRISMA_App
<img width="468" height="621" alt="image" src="https://github.com/user-attachments/assets/9408a05a-0b7b-4eb6-b8b7-eada17940a20" />

# 2. Configure Local Model
ollama create prisma-engine -f Modelfile

# 3. Install Dependencies & Launch UI
pip install streamlit plotly numpy requests
streamlit run app.py

---
## 📄 License & Open-Source Commitment
This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
