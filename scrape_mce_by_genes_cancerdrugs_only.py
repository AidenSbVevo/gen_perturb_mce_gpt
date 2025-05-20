# import argparse
# import re
# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from tqdm import tqdm

# def retrieve_info_for_gene(gene, driver):
#     """
#     1) Navigates to MedChemExpress and searches for `gene`.
#     2) Locates the 'Cancer' filter label, extracts the parentheses number (e.g. 371).
#     3) Clicks the 'Cancer' filter.
#     4) Attempts to read the big number from <div class="search_type_content"><p>...</p></div>.
#     5) If the big number fails, fallback to the parentheses count.
    
#     Returns a dict:
#       {
#         "gene": gene,
#         "num_inhibitors_agonists": int,
#       }
#     """
#     entry = {
#         "gene": gene,
#         "num_inhibitors_agonists": 0,
#     }

#     # Step 1: Go to MedChemExpress homepage and search for the gene
#     driver.get("https://www.medchemexpress.com/")
    
#     try:
#         search_bar = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "search_txt"))
#         )
#         search_bar.clear()
#         search_bar.send_keys(gene + Keys.ENTER)
#     except Exception as e:
#         print(f"[{gene}] Could not interact with search bar: {e}")
#         return entry
    
#     # Step 2: Locate the 'Cancer' filter label and parse the parentheses number
#     parentheses_number = 0  # fallback value
#     try:
#         # Wait for the label to be present and visible
#         cancer_label = WebDriverWait(driver, 2).until(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, "label[data-value='Cancer']"))
#         )
#         # The label might look like: <span>Cancer (371)</span>
#         span_text = cancer_label.find_element(By.CSS_SELECTOR, "span").text  # e.g. "Cancer (371)"
        
#         # We'll use a regex to extract the integer in parentheses
#         match = re.search(r"\((\d+)\)", span_text)
#         if match:
#             parentheses_number = int(match.group(1))
#     except Exception as e:
#         print(f"[{gene}] Could not parse parentheses number from Cancer label: {e}")
#         return entry
    
#     # Step 3: Click the 'Cancer' filter
#     try:
#         WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[data-value='Cancer']")))
#         cancer_label.click()
#     except Exception as e:
#         print(f"[{gene}] Could not click on the Cancer label: {e}")
#         # We can fallback to parentheses_number here and return immediately
#         entry["num_inhibitors_agonists"] = parentheses_number
#         return entry

#     # Step 4: Wait for the updated page results (the big number)
#     try:
#         WebDriverWait(driver, 2).until(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, "div.search_type_content > p"))
#         )
#     except Exception as e:
#         print(f"[{gene}] The updated results after clicking Cancer filter did not load in time: {e}")
#         # fallback to parentheses_number
#         entry["num_inhibitors_agonists"] = parentheses_number
#         return entry

#     # Step 5: Attempt to read the "big number" from the <p> element
#     try:
#         count_element = driver.find_element(By.CSS_SELECTOR, "div.search_type_content > p")
#         big_number_text = count_element.text.strip()
#         big_number_text = big_number_text.replace(",", "")
#         entry["num_inhibitors_agonists"] = int(big_number_text)
#     except Exception as e:
#         print(f"[{gene}] Could not parse the big number, fallback to parentheses count: {e}")
#         entry["num_inhibitors_agonists"] = parentheses_number

#     return entry


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Single-process script: Cancer parentheses fallback + big number.")
#     parser.add_argument("--driver-path", type=str, required=True, 
#                         help="Path to your chromedriver executable.")
#     parser.add_argument("--gene-list", type=str, required=True, 
#                         help="TSV file containing a column named 'Gene'.")
#     parser.add_argument("--output-path", type=str, required=True, 
#                         help="Where to save the output CSV.")
#     args = parser.parse_args()

#     # Initialize Selenium WebDriver
#     service = Service(executable_path=args.driver_path)
#     options = webdriver.ChromeOptions()
#     # If you want headless mode, uncomment the line below:
#     # options.add_argument("--headless=new")
#     options.add_argument("--window-size=1920,1080")
    
#     driver = webdriver.Chrome(service=service, options=options)

#     # Load the gene list
#     df_genes = pd.read_csv(args.gene_list)
#     df_genes = df_genes[df_genes['mce_inhibitors_agonists'] > 0]
#     gene_list = df_genes["Gene"].tolist()

#     # Process each gene in a single loop (single-process)
#     results = []
#     for gene in tqdm(gene_list, desc="Processing genes"):
#         info = retrieve_info_for_gene(gene, driver)
#         results.append(info)

#     # Save results
#     out_df = pd.DataFrame(results)
#     out_df.to_csv(args.output_path, index=False)

#     driver.quit()


# import argparse
# import re
# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from tqdm import tqdm
# import concurrent.futures

# def retrieve_info_for_gene(gene, driver):
#     """
#     1) Navigates to MedChemExpress and searches for `gene`.
#     2) Locates the 'Cancer' filter label, extracts the parentheses number (e.g. 371).
#     3) Clicks the 'Cancer' filter.
#     4) Attempts to read the big number from <div class="search_type_content"><p>...</p></div>.
#     5) If the big number fails, fallback to the parentheses count.
    
#     Returns a dict:
#       {
#         "gene": gene,
#         "num_inhibitors_agonists": int,
#       }
#     """
#     entry = {
#         "gene": gene,
#         "num_inhibitors_agonists": 0,
#     }

#     # Step 1: Go to MedChemExpress homepage and search for the gene
#     driver.get("https://www.medchemexpress.com/")
    
#     try:
#         search_bar = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "search_txt"))
#         )
#         search_bar.clear()
#         search_bar.send_keys(gene + Keys.ENTER)
#     except Exception as e:
#         print(f"[{gene}] Could not interact with search bar: {e}")
#         return entry
    
#     # Step 2: Locate the 'Cancer' filter label and parse the parentheses number
#     parentheses_number = 0  # fallback value
#     try:
#         # Wait for the label to be present and visible.
#         cancer_label = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, "label[data-value='Cancer']"))
#         )
#         # The label might look like: <span>Cancer (371)</span>
#         span_text = cancer_label.find_element(By.CSS_SELECTOR, "span").text  # e.g. "Cancer (371)"
        
#         # Use regex to extract the integer inside parentheses.
#         match = re.search(r"\((\d+)\)", span_text)
#         if match:
#             parentheses_number = int(match.group(1))
#     except Exception as e:
#         print(f"[{gene}] Could not parse parentheses number from Cancer label: {e}")
#         return entry
    
#     # Step 3: Click the 'Cancer' filter
#     try:
#         WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, "label[data-value='Cancer']"))
#         )
#         cancer_label.click()
#     except Exception as e:
#         print(f"[{gene}] Could not click on the Cancer label: {e}")
#         # Fallback to parentheses number if click fails.
#         entry["num_inhibitors_agonists"] = parentheses_number
#         return entry

#     # Step 4: Wait for the updated page results (the big number)
#     try:
#         WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, "div.search_type_content > p"))
#         )
#     except Exception as e:
#         print(f"[{gene}] The updated results after clicking Cancer filter did not load in time: {e}")
#         # Fallback to parentheses number if updated results not loaded.
#         entry["num_inhibitors_agonists"] = parentheses_number
#         return entry

#     # Step 5: Attempt to read the "big number" from the <p> element.
#     try:
#         count_element = driver.find_element(By.CSS_SELECTOR, "div.search_type_content > p")
#         big_number_text = count_element.text.strip().replace(",", "")
#         entry["num_inhibitors_agonists"] = int(big_number_text)
#     except Exception as e:
#         print(f"[{gene}] Could not parse the big number, fallback to parentheses count: {e}")
#         entry["num_inhibitors_agonists"] = parentheses_number

#     return entry

# def process_chunk(chunk, driver_path):
#     """
#     Processes a list of genes in the given chunk using its own Selenium driver.
#     Returns a list of dictionaries with the retrieved information.
#     """
#     # Initialize Selenium WebDriver for this process.
#     service = Service(executable_path=driver_path)
#     options = webdriver.ChromeOptions()
#     # Uncomment the line below to run headless if desired:
#     # options.add_argument("--headless=new")
#     options.add_argument("--window-size=1920,1080")
#     driver = webdriver.Chrome(service=service, options=options)

#     results = []
#     for gene in chunk:
#         info = retrieve_info_for_gene(gene, driver)
#         results.append(info)
#     driver.quit()
#     return results

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Parallel MedChemExpress scraper with Cancer filter fallback using 10 cores and 200 gene chunks."
#     )
#     parser.add_argument("--driver-path", type=str, required=True, 
#                         help="Path to your chromedriver executable.")
#     parser.add_argument("--gene-list", type=str, required=True, 
#                         help="TSV file (or CSV) containing a column named 'Gene'.")
#     parser.add_argument("--output-path", type=str, required=True, 
#                         help="Where to save the output CSV.")
#     args = parser.parse_args()

#     # Load the gene list from file.
#     df_genes = pd.read_csv(args.gene_list)
#     df_genes = df_genes[df_genes['mce_inhibitors_agonists']>0]
#     gene_list = df_genes["Gene"].tolist()
#     print(f"Processing {len(gene_list)} genes.")

#     # Split the gene list into chunks of ~200 genes.
#     chunk_size = 200
#     chunks = [gene_list[i : i + chunk_size] for i in range(0, len(gene_list), chunk_size)]

#     all_results = []
#     # Use 10 processes concurrently.
#     with concurrent.futures.ProcessPoolExecutor(max_workers=30) as executor:
#         # Submit one process per chunk.
#         future_to_chunk = {
#             executor.submit(process_chunk, chunk, args.driver_path): idx 
#             for idx, chunk in enumerate(chunks)
#         }
#         # Use tqdm to track progress.
#         for future in tqdm(concurrent.futures.as_completed(future_to_chunk), total=len(future_to_chunk), desc="Processing chunks"):
#             try:
#                 chunk_results = future.result()
#                 all_results.extend(chunk_results)
#             except Exception as exc:
#                 print(f"A chunk generated an exception: {exc}")

#     # Combine all results and write to CSV.
#     out_df = pd.DataFrame(all_results)
#     out_df.to_csv(args.output_path, index=False)


#!/usr/bin/env python3
import argparse
import re
import pandas as pd
import numpy as np
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

def retrieve_info_for_gene(gene, driver):
    """
    1) Search for gene.
    2) Read the real gene name from the page header.
    3) Locate 'Cancer' filter label, extract parentheses count.
    4) Click 'Cancer'.
    5) Try to parse the big number.
    6) On failure, use the parentheses count.
    """
    entry = {"gene": gene, "num_inhibitors_agonists": np.nan}

    # 1) Go to homepage and search
    driver.get("https://www.medchemexpress.com/")
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "search_txt"))
        )
        search_bar.clear()
        search_bar.send_keys(gene + Keys.ENTER)
    except Exception as e:
        print(f"[{gene}] ▶ search bar error: {e}")
        return entry

    # 2) Read the actual gene name from the results header
    try:
        real_gene = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.search_rst_brief h1"))
        ).text.strip()
        entry["gene"] = real_gene
    except Exception:
        # if it fails, stick with the original
        pass

    # 3) Locate 'Cancer' filter and extract parentheses number
    try:
        cancer_label = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "label[data-value='Cancer']"))
        )
        span_text = cancer_label.find_element(By.CSS_SELECTOR, "span").text  # e.g. "Cancer (1)"
        fallback = int(re.search(r"\((\d+)\)", span_text).group(1))
    except Exception as e:
        print(f"[{entry['gene']}] ▶ could not locate Cancer label: {e}")
        return entry

    # 4) Click the 'Cancer' filter
    try:
        cancer_label.click()
    except Exception as e:
        print(f"[{entry['gene']}] ▶ could not click Cancer filter: {e}")
        entry["num_inhibitors_agonists"] = fallback
        return entry

    # 5) Wait for filtered results
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.search_type_content > p"))
        )
    except Exception as e:
        print(f"[{entry['gene']}] ▶ filtered results did not load: {e}")
        entry["num_inhibitors_agonists"] = fallback
        return entry

    # 6) Parse the big number, else fallback
    try:
        count_el = driver.find_element(By.CSS_SELECTOR, "div.search_type_content > p")
        text = count_el.text.strip().replace(",", "")
        entry["num_inhibitors_agonists"] = int(text)
    except Exception as e:
        print(f"[{entry['gene']}] ▶ parsing big number failed, using fallback: {e}")
        entry["num_inhibitors_agonists"] = fallback

    return entry

def process_gene(gene, driver_path):
    # each worker gets its own Chrome instance
    service = Service(executable_path=driver_path)
    opts = webdriver.ChromeOptions()
    # opts.add_argument("--headless")      # un-comment to run headless
    # opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=opts)

    result = retrieve_info_for_gene(gene, driver)
    driver.quit()
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parallel MCE scraper (gene,count) CSV → TXT, one-browser-per-gene"
    )
    parser.add_argument("--driver-path", required=True, help="Path to chromedriver")
    parser.add_argument("--gene-list",  required=True, help="CSV file with a 'Gene' column")
    parser.add_argument("--output-path", required=True, help="Output TXT path")
    args = parser.parse_args()

    # 1) Read all your genes
    df = pd.read_csv(args.gene_list)
    df = df[df['mce_inhibitors_agonists'] > 0]
    genes = df["Gene"].tolist()

    # 2) Fire off one browser per gene in parallel
    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as exe:
        for rec in tqdm(
            exe.map(process_gene, genes, [args.driver_path]*len(genes)),
            total=len(genes),
            desc="Genes"
        ):
            all_results.append(rec)

    # 3) Dump to simple TXT: gene,count
    with open(args.output_path, "w") as fout:
        for r in all_results:
            fout.write(f"{r['gene']},{r['num_inhibitors_agonists']}\n")
