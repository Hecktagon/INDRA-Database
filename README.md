# Quick Start Guide  

1. This program requires the indra and pandas libraries, which you need to download by typing `pip install indra` and `pip install pandas` in your terminal.  

2. Run `main.py` to start the program, it will prompt you for all needed information. Outputs will be printed to the console, but as of right now are not saved to any files.

# indra_queries.py  

## Public Methods

### `get_interactions(...)`
Look up interactions involving one or two genes.

| Parameter | What it means |
|-----------|---------------|
| `subject` | The gene *doing* something — e.g. `"MAP2K1"` in "MAP2K1 phosphorylates X" |
| `object` | The gene *receiving* the action — e.g. `"MAPK1"` in "X phosphorylates MAPK1" |
| `agents` | A list of genes involved in any role — use when you don't care who's doing what |
| `stmt_type` | Filter by relationship type, e.g. `"Phosphorylation"`, `"Inhibition"`, `"Activation"` |
| `limit` | Maximum number of results to return (default: `100`) |

**Returns:** A list of statement objects describing the interactions found.

**Example:**
```python
# What does MAP2K1 phosphorylate?
stmts = get_interactions(subject="MAP2K1", stmt_type="Phosphorylation")

# Any interaction between BRCA1 and TP53
stmts = get_interactions(agents=["BRCA1", "TP53"])
```

---

### `get_interactions_for_many(...)`
Same as `get_interactions`, but for a **list of genes** — fetches them all at once in parallel (faster than calling one at a time).

| Parameter | What it means |
|-----------|---------------|
| `agents_list` | A list of gene names to look up, e.g. `["BRCA1", "TP53", "EGFR"]` |
| `stmt_type` | Filter by relationship type (optional) |
| `limit` | Maximum results per gene (default: `50`) |
| `workers` | How many genes to fetch simultaneously (default: `5`) |

**Returns:** A dictionary where each key is a gene name and each value is the list of statements for that gene. Also prints a summary to the console as results come in.

**Example:**
```python
results = get_interactions_for_many(["BRCA1", "TP53", "EGFR"])
# results["BRCA1"] → list of statements involving BRCA1
```

---

### `get_interactions_from_papers(...)`
Get all interactions found in one or more **specific papers**.

| Parameter | What it means |
|-----------|---------------|
| `paper_ids` | A list of `(id_type, id_value)` tuples identifying the papers. `id_type` can be `"pmid"`, `"pmcid"`, or `"doi"` |
| `limit` | Maximum number of results (default: `100`) |

**Returns:** A list of statement objects extracted from those papers.

**Example:**
```python
stmts = get_interactions_from_papers([("pmid", "22174878")])
```

---

### `get_interactions_by_hash(...)`
Retrieve one or more **specific interactions** you've already identified, using their unique hash numbers.

> **What's a hash?** Every statement has a unique ID number. You can get it by calling `stmt.get_hash()` on any statement you've already retrieved.

| Parameter | What it means |
|-----------|---------------|
| `hashes` | A list of hash numbers identifying the exact statements you want |
| `limit` | Maximum number of results (default: `100`) |

**Returns:** A list of the matching statement objects.

**Example:**
```python
my_hash = stmts[0].get_hash()
specific = get_interactions_by_hash([my_hash])
```

---

### `get_interactions_filtered(...)`
Advanced search using **custom filter combinations**. Useful when you need fine-grained control over what comes back.

| Parameter | What it means |
|-----------|---------------|
| `query` | A filter expression built from the query helpers below |
| `limit` | Maximum number of results (default: `100`) |

**Available filters** (combine with `&` for AND, `|` for OR, `~` for NOT):

| Filter | What it does |
|--------|--------------|
| `HasAgent("BRCA1")` | Must involve this gene |
| `HasType(["Phosphorylation"])` | Must be this relationship type |
| `HasEvidenceBound(["> 10"])` | Must be backed by more than N papers |
| `HasReadings()` | Must come from machine-reading of scientific papers |
| `HasDatabases()` | Must come from curated biological databases |
| `HasOnlySource("reach")` | Must come from one specific source only |
| `FromMeshIds(["D001943"])` | Must come from papers tagged with a specific MeSH term |

**Returns:** A list of statement objects matching all your filters.

**Example:**
```python
query = (
    HasAgent("MEK", namespace="FPLX")
    & HasType(["Inhibition"])
    & HasEvidenceBound(["> 10"])
    & HasReadings()
)
stmts = get_interactions_filtered(query)
```

---

### `curate_interaction(...)`
Flag an interaction as correct or report a problem with it.

| Parameter | What it means |
|-----------|---------------|
| `stmt` | The statement object you want to flag |
| `tag` | One of: `"correct"`, `"grounding"`, `"wrong_relation"`, `"entity_error"` |
| `your_email` | Your email address (used to credit your curation) |
| `description` | Optional note explaining your flag |

**Returns:** Nothing — submits your curation to the INDRA database.

**Example:**
```python
curate_interaction(stmts[0], tag="correct", your_email="you@example.com")
```

---

### `show(stmts)`
Print a list of statements in plain, readable English — handy for quickly inspecting results.

| Parameter | What it means |
|-----------|---------------|
| `stmts` | Any list of statements returned by the functions above |

**Returns:** Nothing — prints to the console.

**Example:**
```python
stmts = get_interactions(subject="MAP2K1")
show(stmts)
# [0] MAP2K1 phosphorylates MAPK3 — evidence count: 47
# [1] MAP2K1 phosphorylates MAPK1 — evidence count: 39
# ...
```

---

### `add_namespace(ids, id_type)`
A utility that formats gene or molecule IDs with the suffix that INDRA expects when searching by a specific ID system (e.g. UniProt, CHEBI).

| Parameter | What it means |
|-----------|---------------|
| `ids` | A single ID string, or a list of ID strings |
| `id_type` | The ID system: `"hgnc"`, `"uniprot"`, `"hgnc_numeric"`, `"fplx"`, `"chebi"`, or `"text"` |

**Returns:** The ID(s) with the correct suffix appended.

**Example:**
```python
add_namespace("P15056", id_type="uniprot")   # → "P15056@UP"
add_namespace(["P15056", "P04637"], id_type="uniprot")  # → ["P15056@UP", "P04637@UP"]
```