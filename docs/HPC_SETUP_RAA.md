# Panduan Setup PrimerLab RAA di HPC
Dokumen ini menjelaskan cara instalasi dan running `PrimerLab` v1.2.0 (Branch: `feat/raa-multi-candidate-ranking`) di lingkungan HPC.

## 1. Persiapan Environment
Pastikan modul Python dan Compiler sudah terpasang di HPC:
```bash
# Contoh pemuatan modul di HPC (sesuaikan dengan sistem HPC Anda)
module load python/3.10
module load gcc/11.2.0
```

## 2. Cloning Repository
Clone repository dan pindah ke branch eksperimental RAA:
```bash
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic
git checkout feat/raa-multi-candidate-ranking
```

## 3. Instalasi Dependensi
Sangat disarankan menggunakan Virtual Environment agar tidak merusak sistem HPC:
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install dependensi utama
pip install -e .
```

## 4. Instalasi ViennaRNA (Krusial untuk RAA)
Jika `pip install` gagal mengompilasi ViennaRNA, gunakan installer resmi atau conda:
```bash
# Menggunakan Conda (Direkomendasikan di HPC)
conda install -c bioconda viennarna
```

## 5. Cara Running
Anda bisa menggunakan CLI atau Python script:

### A. Menggunakan CLI
```bash
primerlab raa --sequence "ATGC..." --config primerlab/config/raa_default.yaml
```

### B. Menggunakan Python Script (Untuk Integrasi Pipeline)
Gunakan contoh di `examples/run_raa_influenza.py`.

---

## Tips untuk Pandemic Preparedness Pipeline
1. **Memory**: RAA Workflow sangat hemat memori (< 1GB RAM).
2. **CPU**: Gunakan minimal 1-2 core untuk proses kalkulasi ViennaRNA yang cepat.
3. **Timeout**: Jika sekuens sangat sulit, tingkatkan `advanced.timeout` di config file.
