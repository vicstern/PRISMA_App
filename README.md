# PRISMA™ — Platform for Reflection, Interpretation, and Synthesis in Multidimensional Assessment

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Edge AI](https://img.shields.io/badge/Inference-100%25_Offline-purple.svg)]()
[![Child Data Sovereignty](https://img.shields.io/badge/Child_Data-Air--Gapped-red.svg)]()
[![Bilingual](https://img.shields.io/badge/UI-ES%20%7C%20EN-0969da.svg)]()

PRISMA™ is an open-source, air-gapped, edge-AI qualitative pedagogical transducer. Designed as a metacognitive mirror, it **illuminates learning as complex human transformation**, recognizing and safeguarding mental health and holistic well-being as both the catalyst and the outcome of the internal balance required for sustainable personal and institutional growth. PRISMA translates and projects brief classroom observations onto an eight-dimensional vector space ($\mathbb{R}^8$) and has the capacity to **create Official report drafts (editable text & Word `.docx`)** aligned to **SEP / NEM**, **International Baccalaureate (IB)**, **UNAM / CCH**, **Cambridge (IGCSE / A-Levels)**, or custom institutional criteria—ready for educator revision—helping preserve teacher time as a sacred asset, 100% offline. 

> *“Shining white light through learners and projecting its refracted colors to reveal the profound journey of their growth.”*  
> *«Hacer brillar luz blanca a través de cada estudiante y proyectar sus colores refractados para revelar el profundo camino de su crecimiento.»*

Developed as the analytical intero-proprioceptive engine of the **ASPIRE® Ecosystem** (INDAUTOR Reg. `03-2026-040710022300-01` | SSRN DOI: [10.2139/ssrn.7310080](https://doi.org/10.2139/ssrn.7310080)).

---

## 🌟 Core Architectural Principles

1. **Human-Always-in-Charge:** PRISMA only suggests transformation hypotheses grounded in factual classroom observations. The educator retains full authority to accept, manually calibrate, or reject every delta.
2. **100% Offline / Air-Gapped Sovereignty:** Runs strictly on local hardware via Ollama with zero external API calls, eliminating cloud telemetry, recurring SaaS token fees, and child privacy risks by design.
3. **Biopsychosocial Safeguards & Critical Alarm Protocol (`ROJO_CRITICO`):** Integrates a non-punitive *State of Educability* baseline (sleep, nutrition, somatic discomfort/dysmenorrhea/care burdens) to dampen punitive misdiagnosis and recognize resilience under fatigue. If a narrative reveals imminent vital risk, PRISMA immediately halts scoring (`0.0 dB`), triggers an urgent safeguarding alert, and lets the educator log the event without altering the vector.
4. **Logarithmic $\mathbb{R}^8$ Vector Space:** Maps multidimensional growth using Weber-Fechner decibel scaling ($\Delta\text{dB} = 20 \cdot \log_{10}(1 + g)$, where $+6\text{ dB} = 2\times$ baseline capability) across 8 dialectically balanced axes.
5. **Double-Work Elimination (Curricular Translator):** Converts a student's accumulated JSON record into ready-to-use formative reports aligned to **SEP / NEM**, **International Baccalaureate (IB)**, **UNAM / CCH**, **Cambridge (IGCSE / A-Levels)**, or custom institutional criteria, with clean copy-paste output and direct **Word (`.docx`)** export.

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

## 🚀 Quickstart & Hardware-Aware Local Setup

### Prerequisites
- **Python 3.9+** ([python.org](https://www.python.org/downloads/))
- **Ollama** installed locally ([ollama.com/download](https://ollama.com/download))
- **Hardware Tiers:**
  - **PRISMA 4B** (`Qwen3.5-4B`, ~2.71 GB): Recommended for **8 GB RAM** laptops (Apple Silicon M1+, standard Windows/Linux).
  - **PRISMA 9B** (`Qwen3.5-9B`, ~5.63 GB): Recommended for **16+ GB RAM** machines for deeper analytical nuance and broader multilingual fidelity.
- **Native Bilingual Engines (`EN` | `ES`, 0 GB extra disk space):** Each installation automatically compiles dedicated English (`-en`) and Spanish (`-es`) engines from the exact same local `.gguf` weights via Ollama layer deduplication (`Modelfile.en` / `Modelfile.es`). Teachers can write notes in English, Spanish, or any natively supported language and receive consistent output in the active interface language.

### 1. Clone or Download the Repository
```bash
git clone [https://github.com/vicstern/PRISMA_App.git](https://github.com/vicstern/PRISMA_App.git)
cd PRISMA_App
```
*(Or click **Code → Download ZIP** on GitHub and unzip the folder.)*

### 2. Run the Automatic Installer & Launcher

| Operating System | File to Use | First Run & Daily Launch | Add / Switch Models Later |
| :--- | :--- | :--- | :--- |
| **macOS & Linux** | `install_and_run.sh` | `bash install_and_run.sh` | `bash install_and_run.sh --models` |
| **Windows** | `install_and_run.bat` | Double-click `install_and_run.bat` | `install_and_run.bat --models` |

> **What happens on first launch:** The script automatically detects your system RAM, recommends the optimal engine (**4B** for $\le 8\text{ GB}$ RAM or **9B** for $> 8\text{ GB}$ RAM, or lets you install **both**), creates an isolated `.venv`, installs dependencies (including `python-docx`), downloads the verified GGUF weights from [`vicstern/PRISMA-Models`](https://huggingface.co/vicstern/PRISMA-Models), compiles the local Ollama engine(s), and opens PRISMA™ at `http://localhost:8501`.
>
> **100% Offline Operation:** After the initial setup, no internet connection is required. Running the launcher again starts PRISMA™ offline in seconds.

---

## 🌍 Bilingual Interface & Offline Language Matrix

- **Persistent Bilingual UI (`ES` | `EN`):** Switch between Spanish and English in the sidebar at any time without losing active student records. Preferences (`lang`, `modelo_activo`) persist locally in `~/PRISMA_App/config.json`, and student JSON records remain fully cross-compatible between languages.
- **Native SLM Language Coverage (Qwen 3.5 4B / 9B):**
  - **Optimal:** Spanish, English, French, Portuguese, German, Italian, Chinese, Japanese, Korean, Arabic.
  - **Functional (enhanced on 9B):** Catalan, Galician, Basque, Russian, Hindi, Turkish, Dutch.
- **Indigenous & Low-Resource Languages (Air-Gapped Companions):** To preserve zero-cloud child data sovereignty when documenting in indigenous or regional languages, educators may pair PRISMA™ with offline open-source translators such as **Firefox Translations (Bergamot)**, **Argos Translate / LibreTranslate (local)**, or **Meta NLLB-200 (local)**.

---

## 📁 Local Data Storage & Admin Controls

- **Student Records (Air-Gapped):** All longitudinal student JSON files are saved locally in `~/PRISMA_App/expedientes` (outside the Git repository) and never leave the educator's machine.
- **Cycle Closing Lock (Local Safeguard):** The sidebar includes a local administrative safeguard (`prisma2026`) solely to prevent accidental end-of-cycle vector resets (*Tabula Rasa*) during classroom use.

---

## 🛡️ Pedagogical Scope Notice

PRISMA™ is strictly an educational reflection, qualitative learning-analytics, and curricular reporting instrument designed to strengthen teaching quality and holistic student growth. It is **not** a medical, clinical, or psychological diagnostic tool, nor a substitute for qualified healthcare or mental-health professionals.

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

> **[𓆣](./SPECTRUM.md) Live Interactive Edition — PRISMA™ Rosetta Codex**  
> Experience these 23+7 tongues in motion—complete with calligraphic glyphs, live EN/ES comparison, and hidden portal keys—at **[aulaviva.lat](https://aulaviva.lat/)** 

---
