"""
indra_queries.py
~~~~~~~~~~~~~~~~
Simple, readable wrappers around the INDRA package's built-in database client.

Setup:
    pip install indra
    export INDRA_DB_REST_URL="https://db.indra.bio"
    export INDRA_DB_REST_API_KEY="your_key_here"

Usage:
    from indra_queries import *
    stmts = get_interactions(subject="MAP2K1", stmt_type="Phosphorylation")
"""

from indra.sources.indra_db_rest.api import (
    get_statements,
    get_statements_for_papers,
    get_statements_by_hash,
    get_statements_from_query,
    submit_curation,
)
from indra.sources.indra_db_rest.query import (
    HasAgent, HasType, HasEvidenceBound,
    HasReadings, HasDatabases, HasOnlySource,
    FromMeshIds, FromPapers,
)
from concurrent.futures import ThreadPoolExecutor, as_completed


# ----------------------------------------------------------------------
# 1. Get interactions involving one or two genes
#
#   subject   = the gene DOING something       (e.g. "MAP2K1 phosphorylates X")
#   object    = the gene receiving the action  (e.g. "X phosphorylates MAPK1")
#   agents    = list of genes in any role      (e.g. any interaction containing BRCA1 and BRCA2)
#   stmt_type = filter by relationship type    (e.g. "Phosphorylation")
#   limit     = maximum statements to return
# ----------------------------------------------------------------------
def get_interactions(subject=None, object=None, agents=None,
                     stmt_type=None, limit=100):
    p = get_statements(
        subject=subject,
        object=object,
        agents=agents,
        stmt_type=stmt_type,
        limit=limit,
    )
    return p.statements

# ----------------------------------------------------------------------
# 1. (threaded) Get interactions per gene involving a list of genes
#
#   agents    = genes in any role              (e.g. any interaction with BRCA1)
#   stmt_type = filter by relationship type    (e.g. "Phosphorylation")
#   limit     = maximum statements to return per gene
# ----------------------------------------------------------------------
def get_interactions_for_many(agents_list, stmt_type=None, limit=50, workers=5):
    """Fetch interactions for a list of agents in parallel."""
    results = {}

    def fetch_one(agent):
        p = get_statements(agents=[agent], stmt_type=stmt_type,
                           limit=limit, persist=False)
        return agent, p.statements

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_one, a): a for a in agents_list}
        for future in as_completed(futures):
            agent, stmts = future.result()
            results[agent] = stmts
            print(f"{'✓' if stmts else '✗'} {agent} — {len(stmts)} statements")

    return results


# ----------------------------------------------------------------------
# 2. Get interactions from a specific paper
#
#   paper_ids = list of (id_type, id_value) tuples
#   id types  = "pmid", "pmcid", "doi"
#
#   Example: get_interactions_from_papers([("pmid", "22174878")])
# ----------------------------------------------------------------------
def get_interactions_from_papers(paper_ids, limit=100):
    p = get_statements_for_papers(paper_ids, limit=limit)
    return p.statements


# ----------------------------------------------------------------------
# 3. Get a specific interaction by its hash
#
#   hashes = list of statement hash numbers (found in any query result
#            by calling stmt.get_hash() on any statement object)
# ----------------------------------------------------------------------
def get_interactions_by_hash(hashes, limit=100):
    p = get_statements_by_hash(hashes, limit=limit)
    return p.statements


# ----------------------------------------------------------------------
# 4. Advanced search with filters
#
#   Combine any of these filters using & (and), | (or), ~ (not):
#
#   HasAgent("BRCA1")               — involves this gene
#   HasType(["Phosphorylation"])    — this relationship type
#   HasEvidenceBound(["> 10"])      — backed by more than 10 papers
#   HasReadings()                   — from machine-reading of papers
#   HasDatabases()                  — from curated databases
#   HasOnlySource("reach")          — from one specific source only
#   FromMeshIds(["D001943"])        — from papers tagged with a MeSH term
# ----------------------------------------------------------------------
def get_interactions_filtered(query, limit=100):
    p = get_statements_from_query(query, limit=limit)
    return p.statements


# ----------------------------------------------------------------------
# 5. Flag a statement as correct or report an error
#
#   tag options: "correct", "grounding", "wrong_relation", "entity_error"
# ----------------------------------------------------------------------
def curate_interaction(stmt, tag, your_email, description=""):
    submit_curation(
        hash_val=stmt.get_hash(),
        tag=tag,
        curator_email=your_email,
        text=description,
        pa_json=stmt.to_json(),
    )


# ----------------------------------------------------------------------
# Helper: print a list of statements in plain English
# ----------------------------------------------------------------------
def show(stmts):
    if not stmts:
        print("No statements found.")
        return
    for i, s in enumerate(stmts):
        print(f"[{i}] {s} — evidence count: {len(s.evidence)}")


NAMESPACE_SUFFIXES = {
    "hgnc": "",  # default, no suffix needed
    "uniprot": "@UP",
    "hgnc_numeric": "@HGNC",
    "fplx": "@FPLX",
    "chebi": "@CHEBI",
    "text": "@TEXT",
}


# ----------------------------------------------------------------------
# Helper: adds namespace suffix to ids
# ----------------------------------------------------------------------
def add_namespace(ids, id_type="uniprot"):
    """
    Add the appropriate INDRA namespace suffix to one or more IDs.

    ids     : str or list of str
    id_type : one of "hgnc", "uniprot", "hgnc_numeric", "fplx", "chebi", "text"
    """
    if id_type not in NAMESPACE_SUFFIXES:
        raise ValueError(f"Unknown id_type '{id_type}'. "
                         f"Choose from: {list(NAMESPACE_SUFFIXES)}")

    suffix = NAMESPACE_SUFFIXES[id_type]

    if isinstance(ids, str):
        return ids + suffix
    return [i + suffix for i in ids]


# ----------------------------------------------------------------------
# Example usage (remove or modify as needed)
# ----------------------------------------------------------------------
if __name__ == "__main__":

    # "What does MAP2K1 phosphorylate?"
    stmts = get_interactions(subject="MAP2K1", stmt_type="Phosphorylation")
    show(stmts)

    # "Any known interaction between BRCA1 and TP53"
    stmts = get_interactions(agents=["BRCA1", "TP53"])
    show(stmts)

    # "All statements from a specific paper"
    stmts = get_interactions_from_papers([("pmid", "22174878")])
    show(stmts)

    # "MEK inhibitions, backed by more than 10 papers, from machine reading only"
    query = (
        HasAgent("MEK", namespace="FPLX")
        & HasType(["Inhibition"])
        & HasEvidenceBound(["> 10"])
        & HasReadings()
    )
    stmts = get_interactions_filtered(query)
    show(stmts)