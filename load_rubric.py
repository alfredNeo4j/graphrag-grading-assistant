"""Step 1: load rubric.json into Neo4j as Rubric -> Criterion -> Level."""
import json

from db import get_driver, run

CONSTRAINTS = [
    "CREATE CONSTRAINT rubric_id IF NOT EXISTS FOR (r:Rubric) REQUIRE r.rubricId IS UNIQUE",
    "CREATE CONSTRAINT criterion_id IF NOT EXISTS FOR (c:Criterion) REQUIRE c.criterionId IS UNIQUE",
    "CREATE CONSTRAINT level_id IF NOT EXISTS FOR (l:Level) REQUIRE l.levelId IS UNIQUE",
    "CREATE INDEX level_score IF NOT EXISTS FOR (l:Level) ON (l.score)",
    "CREATE FULLTEXT INDEX level_descriptor_fulltext IF NOT EXISTS FOR (l:Level) ON EACH [l.descriptor]",
]

LOAD = """
MERGE (r:Rubric {rubricId: $rubric.rubricId})
  SET r.title = $rubric.title
WITH r
UNWIND $rubric.criteria AS crit
  MERGE (c:Criterion {criterionId: crit.criterionId})
    SET c.name = crit.name, c.weight = crit.weight
  MERGE (r)-[:HAS_CRITERION]->(c)
  WITH c, crit
  UNWIND crit.levels AS lvl
    MERGE (l:Level {levelId: c.criterionId + '-' + toLower(lvl.label)})
      SET l.label = lvl.label, l.score = lvl.score, l.descriptor = lvl.descriptor
    MERGE (c)-[:HAS_LEVEL]->(l)
"""

if __name__ == "__main__":
    with open("rubric.json") as f:
        rubric = json.load(f)
    driver = get_driver()
    for stmt in CONSTRAINTS:
        run(driver, stmt)
    run(driver, LOAD, rubric=rubric)
    print(run(driver, """
        MATCH (r:Rubric)-[:HAS_CRITERION]->(c)-[:HAS_LEVEL]->(l)
        RETURN r.title AS rubric, count(DISTINCT c) AS criteria, count(l) AS levels
    """))
    driver.close()
