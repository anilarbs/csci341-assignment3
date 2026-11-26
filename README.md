# CSCI 341 • Assignment 3
## Research Conference and Paper Review Management System

The PostgreSQL database follows Assignment 3 Appendix A. FastAPI serves the ConfAdmin administrative dashboard at `/` and interactive API documentation at `/docs`. Users, papers, completed reviews and sessions each support list, detail, create, full update and delete. All data in this project are fictional.

## Run on Windows, macOS or Linux with Docker Compose

1. Extract the ZIP into one directory and open a terminal there.
2. Create a plain-text file named `.env` next to `compose.yaml`. Give it one line, `POSTGRES_PASSWORD=` followed by a password of your choice. Use letters and digits in this local recipe so the database URL needs no escaping.
3. Run `docker compose up --build -d`. Open http://localhost:8000/docs. The PostgreSQL volume persists across application restarts. On its first startup, PostgreSQL runs the same three SQL scripts used by the Python initializer.
4. Run `docker compose exec web python part2.py` to see all numbered statements and results. To capture the transcript, append `> my-results.txt`. Run `docker compose exec web python verify_seed.py` to check the original sample.
5. On a disposable seeded copy, run `docker compose exec web python demo_api.py` to exercise all four CRUD workflows and invalid operations. The demonstration deletes its temporary records after a successful run. Identity sequences advance as usual.

To restore the seed without overwriting the first database, run `docker compose -p csci341fresh up --build -d` after stopping the first stack with `docker compose stop`. Use the same `-p csci341fresh` option in subsequent Compose commands for this copy. Choose a new project name for each fresh volume. The standalone restore procedure below also works in an empty PostgreSQL database.

## Run without Docker / restore the SQL export

Tested with Python 3.12, PostgreSQL 16.2, SQLAlchemy 2.1.9, psycopg 3.3.9, FastAPI 0.141.1, Pydantic 2.13.4 and Uvicorn 0.52.1. Exact Python dependencies are in requirements.txt. The SQL file is a plain pg_dump export from PostgreSQL 16.2 and includes seed records, identity sequence values, indexes, constraints and the schedule view.

1. Create a new empty PostgreSQL database named `conference` owned by the application user. Use a login with permission to create schemas for the independent Part 2 demonstration.
2. Run `python -m venv .venv` and activate it (Windows PowerShell: `.\.venv\Scripts\Activate.ps1`; bash: `source .venv/bin/activate`). Run `python -m pip install -r requirements.txt`.
3. Set the SQLAlchemy connection URL. PowerShell example: `$env:DATABASE_URL="postgresql+psycopg://conference:PASSWORD@localhost:5432/conference"`. In bash use `export DATABASE_URL='postgresql+psycopg://conference:PASSWORD@localhost:5432/conference'`. Replace the credentials. URL-encode special characters in credentials.
4. Choose **one** initialization path for that empty database. Run `python db.py` to create it through SQLAlchemy, or restore with `psql -X -v ON_ERROR_STOP=1 --single-transaction -h localhost -U conference -d conference -f assignment3.sql`. Both initialize the same schema, data and view. An accidental second initialization fails and rolls back.
5. Run `python verify_seed.py`, then `python part2.py`. Start the web server with `python -m uvicorn app:app --host 0.0.0.0 --port 8000`. Visit http://localhost:8000/docs. In another terminal, run `python demo_api.py` while the local server is listening.
6. To restore after edits, create a second empty database, restore the export into it and point DATABASE_URL to the new database. Restart the app to use the restored database.

## Public deployment and presentation

Deploy the Dockerfile as a web service and provision a persistent PostgreSQL database. Supply the provider's PostgreSQL connection string as the web service's DATABASE_URL, with the provider's SSL settings. The container binds to PORT (default 8000). The container runs start.py, which automatically initializes an empty PostgreSQL database and preserves existing data on subsequent restarts. Restarting the web service never reseeds it. Publish the service, open the public /docs URL in a signed-out browser, and test a read and a disposable write. Keep both services active for grading. The teaching application uses fictional data and requires no login.

The final demonstration video is submitted through Google Drive. Record the deployed application segment at its public URL for the final video, upload the video to Google Drive, grant the graders viewing access and verify both links signed out. Fill in links.txt and the one-page executive summary. Use only actual members' surnames in the ZIP name. One team registration is required, including for a solo submission. The brief sets the registration deadline at November 15 and the assignment deadline at Friday, November 27. Check the course page for the submission time.

## Schema and keys

All fields are mandatory unless listed as optional below. See sql/schema.sql for exact data types, attributes, CHECK expressions and deletion actions. Each conference is one edition. Users have overlapping author/reviewer subtypes and a single affiliation. Values such as room, affiliation and track research area are text. The label tables represent multivalued attributes.

| Relation | Primary key | Foreign keys and special rules |
|---|---|---|
| app_user | user_id | email unique. Stores given name, surname, affiliation, country and phone. |
| author | author_id | Shared key → app_user. ORCID optional. |
| author_research_area | (author_id, area_label) | author_id → author. |
| reviewer | reviewer_id | Shared key → app_user. Integer years_experience ≥ 0. |
| reviewer_expertise | (reviewer_id, area_label) | reviewer_id → reviewer. |
| conference | conference_id | End date ≥ start date. Stores name, acronym, description, city, country and both deadlines. |
| conference_host | (conference_id, host_name) | conference_id → conference. |
| conference_reviewer | (conference_id, reviewer_id) | → conference and reviewer, respectively. |
| track | track_id | conference_id → conference, coordinator_id → reviewer, pair → conference_reviewer. One coordinator. |
| conference_session | session_id | conference_id → conference, chair_id → reviewer, pair → conference_reviewer. End time > start time. |
| paper | paper_id | track_id → track. Optional session_id → conference_session. One session maximum. |
| paper_keyword | (paper_id, keyword) | paper_id → paper. |
| paper_author | (paper_id, author_id) | → paper and author. Positive integer position unique within paper. Partial unique index permits at most one corresponding author. |
| paper_version | (paper_id, version_no) | paper_id → paper. Positive integer version. File location and local upload time required, change note optional. |
| review | review_id | paper_id → paper, reviewer_id → reviewer. Pair unique. Integer score 1–5. Recommendation accept/reject. Confidential comments optional. |

All five paper statuses match the brief, including the space in 'under review'. Every stored review requires a reviewer, paper, score, recommendation, author-facing comments and submission date. The data model has no draft review state. The highest version number is current, including when numbers have gaps. See paper 1 (versions 3 and 1). Local conference times are stored without timezone offsets. The brief supplies no file-storage or authentication requirement. Papers store file locations. No prior group diagrams were supplied; implementation uses Appendix A directly, with the optional pool references and corresponding-author index.

## Integrity and deletion behavior

- Paper and review workflows reject self-reviews in both directions, including edits to existing reviews and paper author lists. A scheduled paper must be accepted and its track must belong to the session's conference. The paper workflow checks changes to status, track and session. The session workflow rejects a conference move that would invalidate an assigned paper. Tracks are read-only. Validation and related writes share a transaction; an error rolls back the entire request. These cross-record application checks assume ordinary sequential grading operations as allowed by the brief. Direct SQL writes bypass application-only checks.
- User POST/PUT requires at least one role, and each selected profile requires one or more labels. Paper POST/PUT requires at least one author, exactly one corresponding author, at least one keyword and one version. Authors and reviewers may exist without papers or reviews. Label and version duplicates are rejected by database keys.
- Every conference in the seed has a track, host and reviewer pool. Minimum conference child counts are seed conventions; these supporting tables are read-only through the API. The database checks pool membership for every coordinator and chair. A reviewer may belong to multiple or zero pools. Reviewers need not coordinate or chair anything. The specification only requires pool membership for chairs and coordinators.
- Deleting a paper cascades to authorship, keywords, reviews and versions. Deleting a session clears its papers' session IDs. Deleting a user cascades to their role rows and labels, but existing authorship, reviews, pool membership, chair or coordinator assignments block deletion of referenced people. Conference deletion is blocked while tracks or sessions reference it. Deleting an otherwise removable conference deletes its host names and pool memberships. Independent users and reviewers survive.
- The database enforces foreign keys, unique keys, checks, required values and at most one corresponding author. The application also rejects blank descriptive input and incomplete lists. A transaction replacing an invalid list restores the previous list on failure.

## Query parameters and expected results

part2.py creates and seeds an isolated schema within a transaction. Each mutation uses its own savepoint that is rolled back immediately. All retrievals and the view use the same original seed. Closing the outer transaction removes the demo schema. The application database remains available during query demonstrations. part2_results.txt is the captured SQL, bound values, per-table counts and results from PostgreSQL.

| Task | Input or population | Result on seed |
|---|---|---|
| 3.1 | arman.armanov@example.com; new phone +77773414141 | One user updated. |
| 3.2 | Astana +7 days; other cities +3 | Oct 20 becomes Oct 27 in Astana and Oct 23 in Almaty. |
| 4.1 | Withdrawn; corresponding email amina.aminova@example.com | Papers 6 and 9 plus dependent rows removed. Paper 6 has Amina in position 2. |
| 4.2 | Empty sessions in Astana | Deletes session 2; sessions 1 and 3 survive. |
| 5.1 | accepted | Papers 1, 2, 7 with corresponding authors. |
| 5.2 | ILIKE '%machine learning%' | Papers 2 and 5 match mixed-case text. |
| 5.3 | paper 1 | Versions 3, 1 in that order. |
| 5.4 | conference 1, Databases, experience ≥ 3 | Reviewer IDs 6, 7, 9. |
| 6.1 | All tracks | (papers, distinct authors): (5,4), (5,5), (0,0), (0,0). |
| 6.2 | All six reviewers | Counts 1, 1, 5, 2, 2, 0. Reviewer 10 has NULL mean. |
| 6.3 | All conferences | SDS: 10 papers, 3 accepted, mean score 39/11 across reviews. AMS: 0, 0, NULL. |
| 6.4 | Average includes zero-review reviewers | Mean 11/6; IDs 7, 8, 9 exceed it. |
| 7 | Accepted / (accepted + rejected) | SDS: 3/(3+2) = 60.00%; AMS: NULL. |
| 8 | Assigned accepted papers | IDs 1 and 7. Accepted paper 2 has no session. |

## Using the interface

Open a method in /docs, select **Try it out** and **Execute**. For a full update, GET the single item and copy its JSON into PUT after removing its top-level ID (the ID is already in the path). Keep nested author_id and version_no. The item endpoints return nested profiles or ordered authors, keywords and versions. Read the selection data at /reference and the live view at /schedule. Use a null session_id to unschedule a paper. A successful delete returns HTTP 204 with an empty body. A missing item returns 404, invalid form or business-rule changes return 422, and database integrity conflicts return 409 with a reason. demo_api.py contains complete example bodies. api_results.txt records an actual POST/GET/PUT/DELETE exercise, checks of both required rejection paths, and rollback after a duplicate keyword.

### Reproducing the restore and full-record rollback tests

Restore assignment3.sql into a fresh database with the standalone restore command above. Point DATABASE_URL to that copy and start the API. Run verify_seed.py, demo_api.py, then verify_seed.py again. The HTTP test records the maximum existing ID for each resource, creates one record in each, and checks all four generated IDs. It also requests a new paper title with a duplicate keyword, verifies that the keyword constraint caused HTTP 409, and compares the complete GET response before and after the rejected edit, including authors and versions. api_results.txt contains the transcript from this clean-restore run.

## Live application

- Administrative dashboard: https://csci341-assignment3-g41x.onrender.com
- Swagger API: https://csci341-assignment3-g41x.onrender.com/docs
- Source repository: https://github.com/anilarbs/csci341-assignment3
- Hosting: Render, Docker, PostgreSQL.
- Authentication: Not required.

All numbered Part 2 SQL operations executed successfully on Render.
The deployed API passed all CRUD, rejection and transaction rollback tests.
The ConfAdmin dashboard uses live PostgreSQL data through the existing API.

