# PRISMA™ — Platform for Reflection and Interpretation in Multidimensional Assessment of Learning

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Edge AI](https://img.shields.io/badge/Inference-100%25_Offline-purple.svg)]()
[![Child Data Sovereignty](https://img.shields.io/badge/Child_Data-Air--Gapped-red.svg)]()

PRISMA™ is an open-source, air-gapped, edge-AI qualitative pedagogical transducer. It is designed to bridge international competency frameworks with community-based learning models. The system analyzes, synthesizes, and maps brief teacher notes, projecting their significance for individual learners’ transformation/growth onto an eight-dimensional vector space ($\mathbb{R}^8$).
Developed as the analytical intero-proprioceptive engine of the **ASPIRE® Ecosystem** (INDAUTOR Reg. 03-2026-040710022300-01 | SSRN DOI: [10.2139/ssrn.7310080](https://doi.org/10.2139/ssrn.7310080)).

---

## 🌟 Core Architectural Principles

1. **Human-Always-in-Charge:** PRISMA only suggests transformation hypotheses based on factual pedagogical observations. The educator maintains inalienable authority to accept, adjust, or reject deltas.
2. **100% Offline / Air-Gapped Sovereignty:** Operates strictly on local hardware with zero external API calls, eliminating cloud telemetry, recurring SaaS token costs, and child privacy risks by design.
3. **Biopsychosocial Safeguards:** Features a non-punitive "State of Educability" baseline (sleep, nutrition, somatic distress/dysmenorrhea/care burdens) to systematically dampen punitive misdiagnosis and recognize resilience under fatigue.
4. **Logarithmic $\mathbb{R}^8$ Vector Space:** Maps multidimensional growth using Weber-Fechner decibel scaling ($\Delta\text{dB} = 20 \cdot \log_{10}(1 + g)$, where $+6\text{ dB} = 2\times$ baseline capability) across 8 complementary axes.

---

## 📐 $\mathbb{R}^8$ Developmental Vector Axes

- **Inquiry & Research** (*Indagación e investigación*)
- **Critical & Analytical Thinking** (*Pensamiento crítico y analítico*)
- **Ethical Reasoning** (*Razonamiento ético*)
- **Intercultural Agency** (*Agencia intercultural*)
- **Collaborative Leadership** (*Liderazgo colaborativo*)
- **Practical & Technical Mastery** (*Saber hacer y ejecución técnica*)
- **Resilience & Self-Management** (*Resiliencia y autogestión*)
- **Metacognitive Reflection** (*Reflexión metacognitiva*)

---

## 🚀 Quickstart & Local Installation (One-Step Setup)

### Prerequisites
- **Python 3.9+** ([python.org](https://www.python.org/downloads/))
- **Ollama** installed locally ([ollama.com/download](https://ollama.com/download))
- **Hardware:** 8 GB RAM minimum (Apple Silicon M1+, modern Windows/Linux laptop) and ~3 GB of free disk space for the quantized model.

### 1. Clone or Download the Repository
```bash
git clone https://github.com/vicstern/PRISMA_App.git
cd PRISMA_App
```
*(Or click the green **Code → Download ZIP** button on GitHub and unzip the folder.)*

### 2. Run the Automatic Installer & Launcher

| Operating System | File to Use | How to Run |
| :--- | :--- | :--- |
| **macOS & Linux** | `install_and_run.sh` | Open Terminal inside the folder and run `bash install_and_run.sh` |
| **Windows** | `install_and_run.bat` | Double-click `install_and_run.bat` (or run it from Command Prompt) |

> **What happens on first launch:** The script creates an isolated `.venv`, installs the 4 Python dependencies (`requirements.txt`), downloads the verified **Qwen 3.5 4B Uncensored (Q4_K_M, ~2.71 GB)** model from [`vicstern/PRISMA-Models`](https://huggingface.co/vicstern/PRISMA-Models), compiles the local `prisma-engine` model in Ollama, and opens PRISMA™ at `http://localhost:8501`.
>
> **Offline operation:** After the first run, the internet connection is no longer needed. Running the same script again starts PRISMA™ offline in seconds.

### Manual Installation (Advanced Users)
```bash
mkdir -p models
curl -fL -o models/Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf \
  https://huggingface.co/vicstern/PRISMA-Models/resolve/main/Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf

ollama create prisma-engine -f Modelfile

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Local Data Storage & Admin Controls

- **Student Records (Air-Gapped):** All student JSON files are saved locally in `~/PRISMA_App/expedientes` (outside the Git repository) and never leave the educator's machine.
- **Cycle Closing Lock (Local Safeguard):** The sidebar includes a local administrative safeguard (`prisma2026`) solely to prevent accidental end-of-cycle vector resets during classroom use.

---

## 🛡️ Pedagogical Scope Notice

PRISMA™ is strictly an educational reflection and qualitative learning-analytics instrument designed to strengthen teaching quality and holistic student growth. It is **not** a medical, clinical, or psychological diagnostic tool, nor a substitute for qualified healthcare or mental-health professionals.

---

## 📄 License & Open-Source Commitment
This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

---

## 🌐 Institutional & Research Ecosystem

**Aula Viva®** — *Sistemas Educativos para el Florecimiento Humano, S.A.S.*
- **Interactive Portal & Sandbox:** [https://aulaviva.lat](https://aulaviva.lat)
- **Model Vault (Hugging Face):** [huggingface.co/vicstern/PRISMA-Models](https://huggingface.co/vicstern/PRISMA-Models)
- **Foundational Paper (SSRN):** [DOI: 10.2139/ssrn.7310080](https://doi.org/10.2139/ssrn.7310080)
- **Institutional Updates:** [Aula Viva® on LinkedIn](https://www.linkedin.com/company/aulaviva-lat)
- **Direct Contact:** [victor@aulaviva.lat](mailto:victor@aulaviva.lat)
- **Principal Systems Architect:** Víctor Stern Rodríguez · INDAUTOR Reg. `03-2026-040710022300-01`

---

[𓆣](./SPECTRUM.md)
