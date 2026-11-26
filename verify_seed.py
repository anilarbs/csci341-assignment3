"""Independent expected results for the unmodified sample and its reporting queries."""
from decimal import Decimal
from sqlalchemy import text
from db import engine
from part2 import QUERIES, PARAMS, TABLES

with engine.connect() as c:
    counts = [c.scalar(text(f"SELECT count(*) FROM {table}")) for table in TABLES]
    assert counts == [10,6,6,6,6,2,2,8,4,3,10,10,14,12,11], counts
    def query(task):
        return c.execute(text(QUERIES[task]),PARAMS.get(task,{})).all()
    assert [r.paper_id for r in query("5.1")] == [1,2,7]
    assert [r.paper_id for r in query("5.2")] == [2,5]
    assert [r.version_no for r in query("5.3")] == [3,1]
    assert [r.reviewer_id for r in query("5.4")] == [6,7,9]
    assert [(r.track_id,r.papers,r.authors) for r in query("6.1")] == [(1,5,4),(2,5,5),(3,0,0),(4,0,0)]
    assert [(r.reviews,r.average_score) for r in query("6.2")] == [(1,2),(1,4),(5,Decimal("3.4")),(2,Decimal("4.5")),(2,Decimal("3.5")),(0,None)]
    primary,empty = query("6.3")
    assert (primary.papers,primary.accepted) == (10,3) and abs(primary.average_score-Decimal(39)/11)<Decimal("1e-15")
    assert (empty.papers,empty.accepted,empty.average_score)==(0,0,None)
    above = query("6.4")
    assert [(r.reviewer_id,r.reviews) for r in above] == [(7,5),(8,2),(9,2)]
    assert all(abs(r.overall_average-Decimal(11)/6)<Decimal("1e-15") for r in above)
    assert [(r.accepted,r.rejected,r.acceptance_rate) for r in query("7")] == [(3,2,60),(0,0,None)]
    assert [r.paper_id for r in query("8")] == [1,7]
    checks = [
        "SELECT 1 FROM app_user u LEFT JOIN author a ON a.author_id=u.user_id LEFT JOIN reviewer r ON r.reviewer_id=u.user_id WHERE a.author_id IS NULL AND r.reviewer_id IS NULL",
        "SELECT 1 FROM paper p WHERE (SELECT count(*) FROM paper_author a WHERE a.paper_id=p.paper_id AND a.is_corresponding)<>1",
        "SELECT 1 FROM review r JOIN paper_author a ON r.paper_id=a.paper_id AND r.reviewer_id=a.author_id",
        "SELECT 1 FROM paper p JOIN track t USING(track_id) JOIN conference_session s USING(session_id) WHERE p.status<>'accepted' OR t.conference_id<>s.conference_id",
    ]
    for parent,child,key in [("author","author_research_area","author_id"),("reviewer","reviewer_expertise","reviewer_id"),
                             ("conference","track","conference_id"),("conference","conference_host","conference_id"),
                             ("conference","conference_reviewer","conference_id"),("paper","paper_version","paper_id"),
                             ("paper","paper_keyword","paper_id")]:
        checks.append(f"SELECT 1 FROM {parent} p WHERE NOT EXISTS (SELECT 1 FROM {child} c WHERE c.{key}=p.{key})")
    for sql in checks:
        assert c.execute(text(sql)).first() is None, sql
print("All seed, retrieval, aggregate and schedule checks passed.")
