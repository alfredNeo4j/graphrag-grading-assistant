"""Step 2: embed every Level.descriptor and create the vector index."""
from db import get_driver, run
from embeddings import DIMENSIONS, embed

if __name__ == "__main__":
    driver = get_driver()
    levels = run(driver, "MATCH (l:Level) RETURN l.levelId AS id, l.descriptor AS text")
    vectors = embed([l["text"] for l in levels])
    rows = [{"id": l["id"], "embedding": v} for l, v in zip(levels, vectors)]
    run(driver, """
        UNWIND $rows AS row
        MATCH (l:Level {levelId: row.id})
        CALL db.create.setNodeVectorProperty(l, 'embedding', row.embedding)
    """, rows=rows)
    run(driver, f"""
        CREATE VECTOR INDEX level_descriptor_idx IF NOT EXISTS
        FOR (l:Level) ON (l.embedding)
        OPTIONS {{indexConfig: {{`vector.dimensions`: {DIMENSIONS}, `vector.similarity_function`: 'cosine'}}}}
    """)
    print(f"Embedded {len(rows)} levels.")
    driver.close()
