# gen_perturb_mce_gpt

This repository provides tools for identifying and annotating druggable genes using MedChemExpress (MCE) and GPT-4. It enables:

- Web scraping of available inhibitors/agonists for a list of genes.
- Filtering for cancer-specific drugs.
- Scoring gene relevance to cancer using GPT-4.

---

## 🚀 Pipeline Overview

### 1. Scrape total drug count for each gene

Uses Selenium to scrape the number of inhibitors/agonists available for each gene on MCE.

**Example:**
```bash
python scrape_mce_by_genes.py \
  --driver-path ~/Downloads/chromedriver-mac-arm64/chromedriver \
  --gene-list genes.csv \
  --output-path mce_drugs.csv


### 2. Filter for cancer-related drugs
Filters the above results to only include those where drugs have been studied or developed in a cancer context using the MCE “Cancer” filter.

**Example:**

```bash
python scrape_mce_by_genes_cancerdrugs_only.py \
  --driver-path ~/Downloads/chromedriver-mac-arm64/chromedriver \
  --gene-list mce_drugs.csv \
  --output-path mce_cancer_only_drugs.csv
