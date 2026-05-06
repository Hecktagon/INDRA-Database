from indra_queries import get_interactions_for_many ,add_namespace
from check_ids_in_indra import *

def get_sample_ids(csv_file, id_column="Accession", sample_size=20):
    ids_df = pd.read_csv(csv_file)
    ids = ids_df[id_column].to_list()
    if sample_size is None:
        return ids
    sample_ids = sample(ids, sample_size)
    return sample_ids


def main(uniprot_ids, statement_type_filter = None, statement_limit_per_gene=15):
    suffixed_ids = add_namespace(uniprot_ids, id_type="uniprot")
    return get_interactions_for_many(suffixed_ids, stmt_type=statement_type_filter, limit=statement_limit_per_gene)


#TODO: this is placeholder logic for inputs, and should be replaced with a nicer way to collect user inputs.
if __name__ == "__main__":
    input_file = input("Enter an input filepath: ")
    id_column_name = input("Enter the name of the ID column in your file (case sensitive): ")
    random_sample_size = input("Enter a random sample size, leave blank to use whole list: ")
    random_sample_size = None if random_sample_size == "" else int(random_sample_size)
    ids_list = get_sample_ids(input_file, id_column=id_column_name, sample_size=random_sample_size)

    statement_limit = input("Enter a per-ID statement limit, leave blank for no limit: ")
    statement_limit = None if statement_limit == "" else int(statement_limit)
    results_dict = main(ids_list, statement_limit_per_gene=statement_limit)

    count_missing = len(ids_list)-len(results_dict)
    for key, val in results_dict.items():
        print(f"{key}: {val}")
        if not val:
            count_missing += 1
    print(f"\nStatements found for {len(ids_list)-count_missing}/{len(ids_list)} genes:")