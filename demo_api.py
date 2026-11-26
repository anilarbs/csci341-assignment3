"""Run against a seeded, disposable copy. Exercises the HTTP API with real requests."""
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

base = os.environ.get("APP_URL", "http://127.0.0.1:8000").rstrip("/")
opener = build_opener(ProxyHandler({}))


def call(method, path, expected, data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = Request(base+path,data=body,method=method,headers={"Content-Type":"application/json"})
    try:
        response = opener.open(request)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read()
        record = json.loads(raw) if raw else None
        print(f"{method} {path} -> {response.status}")
        if response.status != expected:
            raise AssertionError((expected, record))
        if response.status >= 400:
            print("   ",record["detail"])
        return record


def main():
    keys = {"users":"user_id", "sessions":"session_id", "papers":"paper_id", "reviews":"review_id"}
    previous_max = {route:max((r[key] for r in call("GET","/"+route,200)),default=0)
                    for route,key in keys.items()}
    user = dict(given_name="Demo",surname="Scholar",email="a3.demo@example.com",affiliation="Test Institute",
                country="Kazakhstan",phone_number="+77000000000",author={"areas":["Methods"]},
                reviewer={"years_experience":3,"expertise":["Databases"]})
    uid = call("POST","/users",201,user)["user_id"]
    user["phone_number"] = "+77000000001"
    assert call("PUT",f"/users/{uid}",200,user)["phone_number"] == user["phone_number"]
    assert call("GET",f"/users/{uid}",200)["author"]["areas"] == ["Methods"]
    session = dict(conference_id=1,title="Demo talks",session_date="2026-11-18",
                   start_time="13:00",end_time="14:00",room_label="A1",chair_id=7)
    sid = call("POST","/sessions",201,session)["session_id"]
    session["room_label"] = "A2"
    call("PUT",f"/sessions/{sid}",200,session)
    assert call("GET",f"/sessions/{sid}",200)["room_label"] == "A2"
    paper = dict(track_id=1,title="Join plans",abstract="A comparison of join costs.",submission_date="2026-09-10",
                 status="accepted",session_id=sid,keywords=["joins"],
                 authors=[dict(author_id=uid,author_position=1,is_corresponding=True)],
                 versions=[dict(version_no=1,file_location="papers/demo/v1.pdf",uploaded_at="2026-09-10T10:00:00")])
    pid = call("POST","/papers",201,paper)["paper_id"]
    paper["versions"].append(dict(version_no=4,file_location="papers/demo/v4.pdf",uploaded_at="2026-09-12T10:00:00"))
    call("PUT",f"/papers/{pid}",200,paper)
    assert call("GET",f"/papers/{pid}",200)["versions"][0]["version_no"] == 4
    review = dict(paper_id=pid,reviewer_id=7,overall_score=4,recommendation="accept",
                  comments_for_authors="The join cost comparison is clearly reported.",review_submission_date="2026-10-12")
    rid = call("POST","/reviews",201,review)["review_id"]
    for route,new_id in (("users",uid),("sessions",sid),("papers",pid),("reviews",rid)):
        assert new_id > previous_max[route], (route,new_id,previous_max[route])
        print(f"Identity verified: {route} generated {new_id} after maximum {previous_max[route]}.")
    review["overall_score"] = 5
    call("PUT",f"/reviews/{rid}",200,review)
    assert call("GET",f"/reviews/{rid}",200)["overall_score"] == 5
    call("POST","/reviews",422,dict(review,reviewer_id=uid))
    call("PUT",f"/reviews/{rid}",422,dict(review,reviewer_id=uid))
    # Reviewer 6 holds both roles. Existing seed paper 4 has a review by user 6.
    original = call("GET","/papers/4",200)
    changed = {k:v for k,v in original.items() if k!="paper_id"}
    changed["authors"] = changed["authors"]+[dict(author_id=6,author_position=2,is_corresponding=False)]
    call("PUT","/papers/4",422,changed)
    assert call("GET","/papers/4",200) == original
    call("PUT",f"/papers/{pid}",422,dict(paper,status="submitted"))
    call("PUT",f"/papers/{pid}",422,dict(paper,session_id=3))
    call("PUT",f"/papers/{pid}",422,dict(paper,track_id=4))
    call("PUT",f"/sessions/{sid}",422,dict(session,conference_id=2))
    before = call("GET",f"/papers/{pid}",200)
    changed_title = before["title"] + " (rollback test)"
    invalid = dict(paper,title=changed_title,keywords=["joins","joins"])
    error = call("PUT",f"/papers/{pid}",409,invalid)
    assert error["constraint"] == "paper_keyword_pkey", error
    after = call("GET",f"/papers/{pid}",200)
    assert after == before, (before,after)
    print("Complete paper matched before and after rollback, including title, authors, versions and keywords.")
    assert call("GET",f"/sessions/{sid}",200)["conference_id"] == 1
    assert call("GET",f"/reviews/{rid}",200)["reviewer_id"] == 7
    # Removing a session releases its assigned paper.
    for route in [f"/sessions/{sid}",f"/reviews/{rid}",f"/papers/{pid}",f"/users/{uid}"]:
        call("DELETE",route,204)
        call("GET",route,404)
        if route == f"/sessions/{sid}":
            assert call("GET",f"/papers/{pid}",200)["session_id"] is None
    print("Passed all CRUD, rejection and rollback checks.")


if __name__ == "__main__":
    main()
