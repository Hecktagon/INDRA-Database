from indra_queries import get_interactions, get_interactions_for_many ,add_namespace
from check_ids_in_indra import *

def get_random_sample(csv_file, id_column="Accession", sample_size=20):
    ids_df = pd.read_csv(csv_file)
    ids = ids_df[id_column].to_list()
    sample_ids = sample(ids, sample_size)
    return sample_ids


def main(uniprot_ids, statement_type_filter = None, statement_limit_per_gene=15):
    suffixed_ids = add_namespace(uniprot_ids, id_type="uniprot")
    return get_interactions_for_many(suffixed_ids, stmt_type=statement_type_filter, limit=statement_limit_per_gene)


if __name__ == "__main__":
    random_ariel_ids = get_random_sample("Old_Fold_Changes.csv", sample_size=5)
    results_dict = main(random_ariel_ids)
    print(f"\nStatements found for {len(results_dict)}/{len(random_ariel_ids)} genes:")
    for key, val in results_dict.items():
        print(f"{key}: {val}")