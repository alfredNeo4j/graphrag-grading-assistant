"""Step 3: retrieve the rubric levels closest to a student's text, then traverse the graph.
The assistant gives evidence only. It never assigns a grade.

  python grade.py "The poster was cluttered and needed narration"            # vector search
  python grade.py --keyword "cluttered poster requires narration"            # no API key needed
"""
import sys

from db import get_driver, run

VECTOR_QUERY = """
CALL db.index.vector.queryNodes('level_descriptor_idx', $k, $embedding)
YIELD node AS level, score
"""
KEYWORD_QUERY = """
CALL db.index.fulltext.queryNodes('level_descriptor_fulltext', $text, {limit: $k})
YIELD node AS level, score
"""
TRAVERSE = """
MATCH (r:Rubric)-[:HAS_CRITERION]->(c:Criterion)-[:HAS_LEVEL]->(level)
WITH r, c, level, score
ORDER BY score DESC
WITH r, c, collect({label: level.label, score: level.score, similarity: score})[0] AS best
RETURN r.title AS rubric, c.name AS criterion, c.weight AS weight,
       best.label AS level, best.score AS points, best.similarity AS similarity
ORDER BY similarity DESC
"""


def retrieve(driver, text, keyword=False, k=15):
    if keyword:
        return run(driver, KEYWORD_QUERY + TRAVERSE, text=text, k=k)
    from embeddings import embed
    return run(driver, VECTOR_QUERY + TRAVERSE, embedding=embed([text])[0], k=k)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--keyword"]
    if not args:
        sys.exit(__doc__)
    driver = get_driver()
    rows = retrieve(driver, " ".join(args), keyword="--keyword" in sys.argv)
    for r in rows:
        print(f"{r['criterion']:<30} {r['level']:<10} {r['points']}/5  weight={r['weight']:.0%}  sim={r['similarity']:.3f}")
    print("\nThese are closest-matching rubric levels as evidence for the lecturer. The grade is your decision.")
    driver.close()
