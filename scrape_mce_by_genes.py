import argparse
import re
import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import concurrent.futures

def retrieve_info_for_gene(gene, driver):
    """
    1) Navigate to MedChemExpress and search for `gene`.
    2) Wait for stale old result (if any), then wait for new result.
    3) Parse the big number from <div.search_type_content><p>.
    4) On any failure, return 0.
    """
    entry = {
        "gene": gene,
        "num_inhibitors_agonists": 0,
    }

    # 1) Load the homepage
    driver.get("https://www.medchemexpress.com/")

    # Try to grab the old count element so we can wait for it to go stale
    try:
        old_count_el = driver.find_element(By.CSS_SELECTOR, "div.search_type_content > p")
    except Exception:
        old_count_el = None

    # 2) Perform the search
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search_txt"))
        )
        search_bar.clear()
        search_bar.send_keys(gene + Keys.ENTER)
    except Exception as e:
        print(f"[{gene}] ▶ search bar error: {e}")
        return entry

    # 3) Wait for the old result to go stale (if present) or for a new <p> to appear
    try:
        if old_count_el is not None:
            WebDriverWait(driver, 10).until(staleness_of(old_count_el))
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.search_type_content > p"))
        )
    except Exception as e:
        print(f"[{gene}] ▶ result did not load: {e}")
        return entry

    # 4) Parse the new big number
    try:
        count_el = driver.find_element(By.CSS_SELECTOR, "div.search_type_content > p")
        text = count_el.text.strip().replace(",", "")
        entry["num_inhibitors_agonists"] = int(text)
    except Exception as e:
        print(f"[{gene}] ▶ parsing big number failed: {e}")
        entry["num_inhibitors_agonists"] = 0

    return entry

def process_chunk(chunk, driver_path):
    """
    Each process gets its own ChromeDriver and scrapes its chunk of genes.
    """
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)

    results = []
    for gene in chunk:
        results.append(retrieve_info_for_gene(gene, driver))

    driver.quit()
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parallel MedChemExpress scraper with staleness check"
    )
    parser.add_argument("--driver-path", type=str, required=True,
                        help="Path to your chromedriver executable.")
    parser.add_argument("--gene-list", type=str, required=True,
                        help="TSV file with a column named 'Gene'.")
    parser.add_argument("--output-path", type=str, required=True,
                        help="Where to save the output CSV.")
    args = parser.parse_args()

    # Load genes
    df_genes = pd.read_csv(args.gene_list)
    gene_list = df_genes["Gene"].tolist()

    # Split into ~200‑gene chunks
    chunk_size = 200
    chunks = [gene_list[i : i + chunk_size] for i in range(0, len(gene_list), chunk_size)]

    all_results = []
    # 10 parallel processes
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_chunk, ch, args.driver_path) for ch in chunks]
        for fut in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Chunks"):
            try:
                all_results.extend(fut.result())
            except Exception as exc:
                print(f"A chunk generated an exception: {exc}")

    # Combine and reindex into original order
    out_df = pd.DataFrame(all_results)
    out_df = (
        out_df.set_index("gene")
              .reindex(gene_list)       # preserve original ordering
              .reset_index()
    )

    out_df.to_csv(args.output_path, index=False)