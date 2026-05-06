import requests
from main import get_sample_ids

def uniprot_to_kegg(uniprot_ids):
    """Convert a list of UniProt accessions to KEGG gene IDs."""
    # KEGG accepts up to 100 IDs per request, joined by +
    chunk_size = 100
    results = {}

    for i in range(0, len(uniprot_ids), chunk_size):
        chunk = uniprot_ids[i:i + chunk_size]
        query = "+".join(f"uniprot:{uid}" for uid in chunk)
        resp = requests.get(f"https://rest.kegg.jp/conv/genes/{query}")

        if resp.ok and resp.text.strip():
            for line in resp.text.strip().split("\n"):
                uniprot_id, kegg_id = line.split("\t")
                # strip the "uniprot:" prefix from the key
                results[uniprot_id.replace("uniprot:", "")] = kegg_id

    return results


# Example
if __name__ == "__main__":
    ids = get_sample_ids("Old_Fold_Changes.csv", "Accession", 50)
    mapping = uniprot_to_kegg(ids)
    print(f"{len(mapping)}/{len(ids)} mappings found.")
    print(mapping)
    # → {"O08528": "mmu:12387", "P04637": "hsa:7157", ...}