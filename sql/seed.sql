INSERT INTO app_user VALUES
    (1, 'Arman', 'Armanov', 'arman.armanov@example.com', 'Steppe Institute', 'Kazakhstan', '+77010000001'),
    (2, 'Amina', 'Aminova', 'amina.aminova@example.com', 'Altai College', 'Kazakhstan', '+77010000002'),
    (3, 'Dana', 'Karim', 'dana.karim@example.com', 'Steppe Institute', 'Kazakhstan', '+77010000003'),
    (4, 'Ilyas', 'Musa', 'ilyas.musa@example.com', 'Altai College', 'Kazakhstan', '+77010000004'),
    (5, 'Sara', 'Malik', 'sara.malik@example.com', 'Steppe Institute', 'Kazakhstan', '+77010000005'),
    (6, 'Nora', 'Lee', 'nora.lee@example.com', 'Altai College', 'Kazakhstan', '+77010000006'),
    (7, 'Evan', 'Cole', 'evan.cole@example.com', 'Steppe Institute', 'Kazakhstan', '+77010000007'),
    (8, 'Mira', 'Park', 'mira.park@example.com', 'Altai College', 'Kazakhstan', '+77010000008'),
    (9, 'Omar', 'Ali', 'omar.ali@example.com', 'Steppe Institute', 'Kazakhstan', '+77010000009'),
    (10, 'Lena', 'Wu', 'lena.wu@example.com', 'Altai College', 'Kazakhstan', '+77010000010');

INSERT INTO author VALUES
    (1, NULL),
    (2, NULL),
    (3, NULL),
    (4, NULL),
    (5, NULL),
    (6, NULL);

INSERT INTO author_research_area VALUES
    (1, 'Databases'),
    (2, 'Analytics'),
    (3, 'Databases'),
    (4, 'Analytics'),
    (5, 'Databases'),
    (6, 'Analytics');

INSERT INTO reviewer VALUES
    (5, 2),
    (6, 4),
    (7, 8),
    (8, 5),
    (9, 3),
    (10, 0);

INSERT INTO reviewer_expertise VALUES
    (5, 'Databases'),
    (6, 'Databases'),
    (7, 'Databases'),
    (8, 'Systems'),
    (9, 'Databases'),
    (10, 'Databases');

INSERT INTO conference VALUES
    (1, 'Steppe Data Symposium', 'SDS', '2026 research meeting on data methods.', 'Astana', 'Kazakhstan', '2026-11-17', '2026-11-19', '2026-09-15', '2026-10-20'),
    (2, 'Altai Methods Symposium', 'AMS', '2026 research meeting on data methods.', 'Almaty', 'Kazakhstan', '2026-11-17', '2026-11-19', '2026-09-15', '2026-10-20');

INSERT INTO conference_host VALUES
    (1, 'Steppe Institute'),
    (2, 'Altai College');

INSERT INTO conference_reviewer VALUES
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (1, 9),
    (1, 10),
    (2, 7),
    (2, 10);

INSERT INTO track VALUES
    (1, 1, 'Data systems', 'Research on data systems.', 'Data systems', 7),
    (2, 1, 'Learning methods', 'Research on learning methods.', 'Learning methods', 8),
    (3, 1, 'Data ethics', 'Research on data ethics.', 'Data ethics', 9),
    (4, 2, 'Research methods', 'Research on research methods.', 'Research methods', 10);

INSERT INTO conference_session VALUES
    (1, 1, 'Data systems talks', '2026-11-18', '10:00', '11:30', 'Hall 1', 7),
    (2, 1, 'Afternoon panel', '2026-11-18', '10:00', '11:30', 'Hall 2', 8),
    (3, 2, 'Methods forum', '2026-11-18', '10:00', '11:30', 'Hall 3', 7);

INSERT INTO paper VALUES
    (1, 1, 'Skew-aware joins', 'Empirical analysis for skew-aware joins.', '2026-09-10', 'accepted', 1),
    (2, 2, 'Learning index selectivity', 'Machine Learning for learning index selectivity.', '2026-09-10', 'accepted', NULL),
    (3, 1, 'Sparse event streams', 'Empirical analysis for sparse event streams.', '2026-09-10', 'rejected', NULL),
    (4, 1, 'Column-store compression', 'Empirical analysis for column-store compression.', '2026-09-10', 'under review', NULL),
    (5, 2, 'Detecting concept drift', 'Machine Learning for detecting concept drift.', '2026-09-10', 'submitted', NULL),
    (6, 2, 'Small sample classifiers', 'Empirical analysis for small sample classifiers.', '2026-09-10', 'withdrawn', NULL),
    (7, 1, 'Tracing query latency', 'Empirical analysis for tracing query latency.', '2026-09-10', 'accepted', 1),
    (8, 2, 'Stable ranking estimates', 'Empirical analysis for stable ranking estimates.', '2026-09-10', 'rejected', NULL),
    (9, 1, 'Archiving sensor records', 'Empirical analysis for archiving sensor records.', '2026-09-10', 'withdrawn', NULL),
    (10, 2, 'Robust model selection', 'Empirical analysis for robust model selection.', '2026-09-10', 'under review', NULL);

INSERT INTO paper_keyword VALUES
    (1, 'Data systems'),
    (2, 'Learning'),
    (3, 'Data systems'),
    (4, 'Data systems'),
    (5, 'Learning'),
    (6, 'Learning'),
    (7, 'Data systems'),
    (8, 'Learning'),
    (9, 'Data systems'),
    (10, 'Learning');

INSERT INTO paper_author VALUES
    (1, 1, 1, TRUE),
    (1, 2, 2, FALSE),
    (2, 3, 1, TRUE),
    (2, 6, 2, FALSE),
    (3, 3, 1, TRUE),
    (4, 4, 1, TRUE),
    (5, 5, 1, TRUE),
    (6, 1, 1, FALSE),
    (6, 2, 2, TRUE),
    (7, 4, 1, TRUE),
    (7, 1, 2, FALSE),
    (8, 6, 1, TRUE),
    (9, 2, 1, TRUE),
    (10, 3, 1, TRUE);

INSERT INTO paper_version VALUES
    (1, 1, 'papers/1/v1.pdf', '2026-09-10 09:30:00', NULL),
    (1, 3, 'papers/1/v3.pdf', '2026-09-12 09:30:00', 'Revised experiments'),
    (2, 1, 'papers/2/v1.pdf', '2026-09-10 09:30:00', NULL),
    (3, 1, 'papers/3/v1.pdf', '2026-09-10 09:30:00', NULL),
    (4, 1, 'papers/4/v1.pdf', '2026-09-10 09:30:00', NULL),
    (5, 1, 'papers/5/v1.pdf', '2026-09-10 09:30:00', NULL),
    (6, 1, 'papers/6/v1.pdf', '2026-09-10 09:30:00', NULL),
    (6, 3, 'papers/6/v3.pdf', '2026-09-12 09:30:00', 'Revised experiments'),
    (7, 1, 'papers/7/v1.pdf', '2026-09-10 09:30:00', NULL),
    (8, 1, 'papers/8/v1.pdf', '2026-09-10 09:30:00', NULL),
    (9, 1, 'papers/9/v1.pdf', '2026-09-10 09:30:00', NULL),
    (10, 1, 'papers/10/v1.pdf', '2026-09-10 09:30:00', NULL);

INSERT INTO review VALUES
    (1, 1, 7, 5, 'accept', 'Clear analysis and reproducible experiments.', NULL, '2026-10-12'),
    (2, 1, 8, 4, 'accept', 'Clear analysis and reproducible experiments.', NULL, '2026-10-12'),
    (3, 2, 7, 5, 'accept', 'Clear analysis and reproducible experiments.', NULL, '2026-10-12'),
    (4, 3, 7, 2, 'reject', 'Explain the baseline and expand the evaluation.', NULL, '2026-10-12'),
    (5, 3, 9, 3, 'reject', 'Explain the baseline and expand the evaluation.', NULL, '2026-10-12'),
    (6, 4, 6, 4, 'accept', 'Clear analysis and reproducible experiments.', NULL, '2026-10-12'),
    (7, 6, 7, 2, 'reject', 'Explain the baseline and expand the evaluation.', NULL, '2026-10-12'),
    (8, 7, 8, 5, 'accept', 'Clear analysis and reproducible experiments.', NULL, '2026-10-12'),
    (9, 8, 5, 2, 'reject', 'Explain the baseline and expand the evaluation.', NULL, '2026-10-12'),
    (10, 9, 7, 3, 'reject', 'Explain the baseline and expand the evaluation.', NULL, '2026-10-12'),
    (11, 10, 9, 4, 'accept', 'Clear analysis and reproducible experiments.', NULL, '2026-10-12');

SELECT setval(pg_get_serial_sequence('app_user', 'user_id'), (SELECT max(user_id) FROM app_user));
SELECT setval(pg_get_serial_sequence('conference', 'conference_id'), (SELECT max(conference_id) FROM conference));
SELECT setval(pg_get_serial_sequence('track', 'track_id'), (SELECT max(track_id) FROM track));
SELECT setval(pg_get_serial_sequence('conference_session', 'session_id'), (SELECT max(session_id) FROM conference_session));
SELECT setval(pg_get_serial_sequence('paper', 'paper_id'), (SELECT max(paper_id) FROM paper));
SELECT setval(pg_get_serial_sequence('review', 'review_id'), (SELECT max(review_id) FROM review));
