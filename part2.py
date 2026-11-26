"""Run python part2.py. The entire demonstration uses a private transaction."""
from uuid import uuid4
from sqlalchemy import text
from db import engine, statements

TABLES = ("app_user author author_research_area reviewer reviewer_expertise conference "
          "conference_host conference_reviewer track conference_session paper paper_keyword "
          "paper_author paper_version review").split()

QUERIES = {
"5.1": """
SELECT p.paper_id, p.title, u.given_name || ' ' || u.surname AS corresponding_author,
       u.email, t.name AS track_name, c.conference_id, c.acronym
FROM paper p JOIN paper_author a ON a.paper_id=p.paper_id AND a.is_corresponding
JOIN app_user u ON u.user_id=a.author_id JOIN track t USING(track_id)
JOIN conference c USING(conference_id) WHERE p.status=:status ORDER BY p.paper_id""",
"5.2": "SELECT paper_id,title FROM paper WHERE abstract ILIKE :phrase ORDER BY paper_id",
"5.3": """SELECT version_no,file_location,uploaded_at FROM paper_version
WHERE paper_id=:paper ORDER BY version_no DESC""",
"5.4": """
SELECT r.reviewer_id,u.given_name || ' ' || u.surname AS full_name,u.email
FROM conference_reviewer cr JOIN reviewer r USING(reviewer_id)
JOIN app_user u ON u.user_id=r.reviewer_id JOIN reviewer_expertise e USING(reviewer_id)
WHERE cr.conference_id=:conference AND e.area_label=:area AND r.years_experience>=:years
ORDER BY r.reviewer_id""",
"6.1": """
SELECT t.track_id,t.name,t.conference_id,count(DISTINCT p.paper_id) AS papers,
       count(DISTINCT a.author_id) AS authors
FROM track t LEFT JOIN paper p USING(track_id) LEFT JOIN paper_author a USING(paper_id)
GROUP BY t.track_id ORDER BY t.track_id""",
"6.2": """
SELECT r.reviewer_id,u.given_name || ' ' || u.surname AS full_name,
       count(v.review_id) AS reviews,avg(v.overall_score) AS average_score
FROM reviewer r JOIN app_user u ON u.user_id=r.reviewer_id LEFT JOIN review v USING(reviewer_id)
GROUP BY r.reviewer_id,u.user_id ORDER BY r.reviewer_id""",
"6.3": """
SELECT c.conference_id,c.acronym,count(DISTINCT p.paper_id) AS papers,
       count(DISTINCT p.paper_id) FILTER (WHERE p.status='accepted') AS accepted,
       avg(r.overall_score) AS average_score
FROM conference c LEFT JOIN track t USING(conference_id) LEFT JOIN paper p USING(track_id)
LEFT JOIN review r USING(paper_id) GROUP BY c.conference_id ORDER BY c.conference_id""",
"6.4": """
WITH counts AS (
    SELECT r.reviewer_id,count(v.review_id) AS reviews FROM reviewer r
    LEFT JOIN review v USING(reviewer_id) GROUP BY r.reviewer_id
), baseline AS (SELECT avg(reviews) AS overall_average FROM counts)
SELECT c.reviewer_id,u.given_name || ' ' || u.surname AS full_name,c.reviews,b.overall_average
FROM counts c JOIN app_user u ON u.user_id=c.reviewer_id CROSS JOIN baseline b
WHERE c.reviews>b.overall_average ORDER BY c.reviews DESC,c.reviewer_id""",
"7": """
WITH decisions AS (
    SELECT c.conference_id,c.acronym,count(p.paper_id) FILTER (WHERE p.status='accepted') AS accepted,
           count(p.paper_id) FILTER (WHERE p.status='rejected') AS rejected
    FROM conference c LEFT JOIN track t USING(conference_id) LEFT JOIN paper p USING(track_id)
    GROUP BY c.conference_id
)
SELECT *,round(100.0*accepted/nullif(accepted+rejected,0),2) AS acceptance_rate
FROM decisions ORDER BY conference_id""",
"8": """SELECT * FROM accepted_paper_schedule
ORDER BY conference_id,session_date,start_time,session_id,paper_id"""
}
PARAMS = {"5.1":{"status":"accepted"}, "5.2":{"phrase":"%machine learning%"},
          "5.3":{"paper":1}, "5.4":{"conference":1,"area":"Databases","years":3}}

def show(c, sql, params=None):
    print(sql.strip(), params or "", sep="\n")
    result = c.execute(text(sql), params or {})
    if result.returns_rows:
        print(" | ".join(result.keys()))
        rows = result.all()
        for row in rows:
            print(" | ".join("NULL" if value is None else str(value) for value in row))
        print(f"({len(rows)} rows)")
    elif result.rowcount >= 0:
        print(f"({result.rowcount} affected)")
    else:
        print("OK")


def demonstrate(c, task, before, action, params):
    print(f"\nTask {task}")
    savepoint = c.begin_nested()
    try:
        print("Before")
        for sql in before:
            show(c, sql, params)
        show(c, action, params)
        print("After")
        for sql in before:
            show(c, sql, params)
    finally:
        savepoint.rollback()
    print("Rolled back to seed.")


def main():
    with engine.connect() as c:
        # Generated identifier. Schema is invisible to others and rolls back on exit.
        schema = "demo_" + uuid4().hex
        c.exec_driver_sql(f"CREATE SCHEMA {schema}")
        c.exec_driver_sql(f"SET LOCAL search_path TO {schema}")
        for task, filename in [(1,"schema.sql"),(2,"seed.sql")]:
            print(f"Task {task}")
            for sql in statements(filename):
                show(c, sql)
        for table in TABLES:
            show(c, f"SELECT count(*) AS {table}_rows FROM {table}")
        demonstrate(c,"3.1",["SELECT user_id,email,phone_number FROM app_user WHERE email=:email"],
                    "UPDATE app_user SET phone_number=:phone WHERE email=:email",
                    {"email":"arman.armanov@example.com","phone":"+77773414141"})
        demonstrate(c,"3.2",["SELECT conference_id,city,review_deadline FROM conference ORDER BY conference_id"],
                    """UPDATE conference SET review_deadline=review_deadline +
                    CASE WHEN city=:city THEN CAST(:local_days AS integer) ELSE CAST(:other_days AS integer) END""",
                    {"city":"Astana","local_days":7,"other_days":3})
        target = """SELECT p.paper_id FROM paper p JOIN paper_author a USING(paper_id)
                    JOIN app_user u ON u.user_id=a.author_id
                    WHERE p.status=:status AND a.is_corresponding AND u.email=:email"""
        snapshots = ["SELECT paper_id,status FROM paper ORDER BY paper_id"]
        snapshots += [f"SELECT paper_id,count(*) FROM {t} GROUP BY paper_id ORDER BY paper_id"
                      for t in ("paper_keyword","paper_author","paper_version","review")]
        snapshots += [f"SELECT count(*) FROM {t}" for t in ("app_user","track","conference")]
        demonstrate(c,"4.1",snapshots,"DELETE FROM paper WHERE paper_id IN ("+target+") RETURNING paper_id",
                    {"email":"amina.aminova@example.com","status":"withdrawn"})
        demonstrate(c,"4.2",["SELECT session_id,conference_id,title FROM conference_session ORDER BY session_id",
                             "SELECT conference_id,city FROM conference ORDER BY conference_id"],
                    """DELETE FROM conference_session s USING conference c
                    WHERE c.conference_id=s.conference_id AND c.city=:city
                    AND NOT EXISTS (SELECT 1 FROM paper p WHERE p.session_id=s.session_id)
                    RETURNING s.session_id""",{"city":"Astana"})
        for task, sql in QUERIES.items():
            print(f"\nTask {task}")
            if task == "8":
                show(c,statements("view.sql")[0])
            show(c,sql,PARAMS.get(task))


if __name__ == "__main__":
    main()
