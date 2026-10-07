# GraphRAG Grading Assistant (example for lecturers)

Built for the Neo4j GraphRAG Hackathon, 23 Oct. A small starting point: a grading rubric stored as a graph in Neo4j Aura, with vector search over the level descriptors.

    (:Rubric)-[:HAS_CRITERION]->(:Criterion {name, weight})-[:HAS_LEVEL]->(:Level {label, score, descriptor, embedding})

## Setup
    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    # .env: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE, OPENAI_API_KEY

## Run
    .venv/bin/python load_rubric.py          # 1. rubric.json -> graph (1 rubric, 6 criteria, 30 levels)
    .venv/bin/python embed_levels.py         # 2. embed descriptors + vector index (needs OPENAI_API_KEY)
    .venv/bin/python grade.py "feedback text"            # 3. vector search -> traverse -> evidence per criterion (you decide the grade)
    .venv/bin/python grade.py --keyword "feedback text"  #    same, keyword search, no API key

## Design
- The graph holds the rubric, so any rubric works: edit `rubric.json`, nothing else is poster-specific.
- The LLM gives feedback on how well a submission meets each criterion. The grade is always the lecturer's decision.

## Make it yours
- Replace `rubric.json` with your own criteria, weights and levels, then re-run steps 1-2.
- Add your own students and grades, for example
  `(:Student)-[:SUBMITTED]->(:Submission)-[:EVALUATED_BY]->(:Evaluation)-[:SCORES]->(:EvaluationScore)-[:FOR_CRITERION]->(:Criterion)`,
  with `(:EvaluationScore)-[:MATCHED_LEVEL]->(:Level)`.
- Swap the embedding provider in `embeddings.py` (change `DIMENSIONS` to match).
- Feed the retrieved levels to an LLM to draft written feedback (the "generation" half of GraphRAG).
