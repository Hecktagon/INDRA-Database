from indra.sources.indra_db_rest.api import get_statements
import pandas as pd
from random import sample
from main import get_sample_ids

def check_uniprot_ids_in_indra(uniprot_ids):
    """Check which UniProt IDs have any relationships in the INDRA database."""
    found = []
    not_found = []

    for uid in uniprot_ids:
        p = get_statements(agents=[f"{uid}@UP"], limit=1, persist=False)
        if p.statements:
            found.append(uid)
            print(f"✓ {uid} — found ({p.get_ev_count(p.statements[0])} evidence on top result)")
        else:
            not_found.append(uid)
            print(f"✗ {uid} — not found")

    print(f"\n{len(found)}/{len(uniprot_ids)} IDs found in INDRA")
    return found, not_found

if __name__ == "__main__":
    rand_sample_filename = input("Provide a filepath to sample: ")
    sampled_ids = get_sample_ids(rand_sample_filename, sample_size=50)
    found_ids, not_found_ids = check_uniprot_ids_in_indra(sampled_ids)