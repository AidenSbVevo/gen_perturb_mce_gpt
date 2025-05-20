import argparse
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

def query_cancer_relevance_batch(genes, client):
    """
    Query cancer relevance for a batch of gene names.
    The prompt instructs the model to output for each gene one line formatted as:
    GeneName, score, justification
    """
    system_msg = "You are an expert in oncology and genomics."
    task_msg = (
        "I am giving you a list of gene names.\n"
        "For each gene, assign a 1-3 score to indicate its relevance to cancer, where:\n"
        "  1 = not relevant to cancer\n"
        "  2 = partially relevant to cancer\n"
        "  3 = highly relevant to cancer\n\n"
        "Relevance is based on factors such as somatic variants in cancer; "
        "functional and/or phenotypic studies in preclinical models (in vitro and in vivo); "
        "drug development efforts (including at the preclinical stage); and involvement in cancer signaling pathways.\n\n"
        "Output for each gene should be on a new line in the following format:\n"
        "  GeneName, score, justification\n\n"
        "Keep the justification to one or two short sentences that include only the most important information."
    )
    # Prepare the list of genes (one per line)
    gene_list_text = "\n".join(genes)
    user_msg = f"{task_msg}\n\nHere is the list of genes:\n{gene_list_text}"

    # Query the API.
    completion = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4.1" if your account has that model enabled
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )
    
    output_text = completion.choices[0].message.content.strip()
    return output_text

def parse_batch_output(batch_output):
    """
    Parse the output from a batch query.
    Assumes that each non-empty line is formatted as:
    GeneName, score, justification
    The split is done on the first two commas so that commas within justification are allowed.
    """
    results = []
    for line in batch_output.splitlines():
        if not line.strip():
            continue
        parts = line.split(",", 2)  # split into 3 parts maximum
        if len(parts) >= 3:
            gene = parts[0].strip()
            score = parts[1].strip()
            justification = parts[2].strip()
            results.append((gene, score, justification))
        else:
            # If the line doesn't match expected format, include it as a whole justification.
            results.append((line.strip(), "", ""))
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Query cancer relevance information for genes in batches using the OpenAI API."
    )
    parser.add_argument(
        "--input-path", type=str, required=True,
        help="Path to the input CSV file containing gene names."
    )
    parser.add_argument(
        "--output-path", type=str, required=True,
        help="Path to the output text file (comma-separated) where results will be saved."
    )
    parser.add_argument(
        "--column", type=str, default="gene",
        help="Column name in the input CSV that contains gene names (default: 'gene')."
    )
    parser.add_argument(
        "--batch-size", type=int, default=15,
        help="Number of genes per API request (default: 15)."
    )
    args = parser.parse_args()

    # Load genes from the CSV file
    df = pd.read_csv(args.input_path)
    if args.column not in df.columns:
        raise ValueError(f"Column '{args.column}' not found in input file.")
    gene_list = df[args.column].tolist()

    # Initialize the OpenAI API client.
    client = OpenAI()
    # Ensure your API key is set via the environment variable "OPENAI_API_KEY"
    # or by setting: client.api_key = "your-api-key-here" here.

    total = len(gene_list)

    # Open the output file in write mode; results will be appended as each batch finishes.
    with open(args.output_path, "w") as f:
        for i in tqdm(range(0, total, args.batch_size), desc="Processing batches"):
            batch_genes = gene_list[i:i + args.batch_size]
            batch_output = query_cancer_relevance_batch(batch_genes, client)
            batch_results = parse_batch_output(batch_output)
            for gene, score, justification in batch_results:
                f.write(f"{gene}, {score}, {justification}\n")
            f.flush()  # Flush after each batch to ensure data is written to disk.

    print(f"Results saved to {args.output_path}")

if __name__ == "__main__":
    main()
