"""Transactional CRUD. SQL identifiers come only from the definitions in this module."""
from fastapi import HTTPException, Response
from fastapi_offline import FastAPIOffline
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, DataError
from db import engine
from models import User, Paper, Review, Session

app = FastAPIOffline(title="Research Conference Administration", version="1.0",
              description="Open an operation, select Try it out, edit the JSON, then Execute. "
                          "GET an item to see its full record. PUT replaces the full record.")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).with_name("dashboard.html"), media_type="text/html")


@app.exception_handler(IntegrityError)
@app.exception_handler(DataError)
async def database_error(request, exc):
    diag = exc.orig.diag
    return JSONResponse(status_code=409, content={"detail": diag.message_primary,
                        "constraint": diag.constraint_name, "reason": diag.message_detail})


def rows(c, sql, **params):
    return [dict(r) for r in c.execute(text(sql), params).mappings()]


def require(c, table, key, item_id):
    result = rows(c,f"SELECT * FROM {table} WHERE {key}=:id",id=item_id)
    if not result:
        raise HTTPException(404,"Record does not exist.")
    return result[0]


def save_row(c, table, values, key=None, item_id=None):
    fields = list(values)
    if item_id is None:
        sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(':'+f for f in fields)})"
    else:
        sql = f"UPDATE {table} SET " + ", ".join(f"{f}=:{f}" for f in fields) + f" WHERE {key}=:record_id"
        values = dict(values,record_id=item_id)
    if key:
        sql += f" RETURNING {key}"
    result = c.execute(text(sql),values)
    return result.scalar_one() if key else None


def replace_children(c, table, key, item_id, records):
    c.execute(text(f"DELETE FROM {table} WHERE {key}=:id"),{"id":item_id})
    for record in records:
        save_row(c,table,{key:item_id,**record})


PROFILES = [
    ("author","author_id","orcid","author_research_area","areas"),
    ("reviewer","reviewer_id","years_experience","reviewer_expertise","expertise"),
]


def save_user(c, values, user_id):
    profiles = {role:values.pop(role) for role,*_ in PROFILES}
    user_id = save_row(c,"app_user",values,"user_id",user_id)
    for role,key,field,labels,collection in PROFILES:
        profile = profiles[role]
        if profile is None:
            c.execute(text(f"DELETE FROM {role} WHERE {key}=:id"),{"id":user_id})
            continue
        c.execute(text(f"""INSERT INTO {role} ({key},{field}) VALUES (:id,:value)
                     ON CONFLICT ({key}) DO UPDATE SET {field}=excluded.{field}"""),
                  {"id":user_id,"value":profile[field]})
        replace_children(c,labels,key,user_id,[{"area_label":a} for a in profile[collection]])
    return user_id


def reject_if(c, sql, message, **params):
    if c.execute(text(sql),params).first() is not None:
        raise HTTPException(422,message)


def save_paper(c, values, paper_id):
    authors = values.pop("authors")
    versions = values.pop("versions")
    keywords = values.pop("keywords")
    if values["session_id"] is not None:
        if values["status"] != "accepted":
            raise HTTPException(422,"Only accepted papers may be assigned to sessions.")
        reject_if(c,"""SELECT 1 FROM track t,conference_session s WHERE t.track_id=:track
                  AND s.session_id=:session AND t.conference_id<>s.conference_id""",
                  "The track and session belong to different conferences.",
                  track=values["track_id"],session=values["session_id"])
    paper_id = save_row(c,"paper",values,"paper_id",paper_id)
    replace_children(c,"paper_author","paper_id",paper_id,authors)
    reject_if(c,"""SELECT 1 FROM paper_author a JOIN review r ON r.paper_id=a.paper_id
              AND r.reviewer_id=a.author_id WHERE a.paper_id=:id""",
              "A reviewer of this paper cannot be added as an author.",id=paper_id)
    replace_children(c,"paper_version","paper_id",paper_id,versions)
    replace_children(c,"paper_keyword","paper_id",paper_id,[{"keyword":k} for k in keywords])
    return paper_id


def save_review(c, values, review_id):
    reject_if(c,"SELECT 1 FROM paper_author WHERE paper_id=:paper AND author_id=:reviewer",
              "Authors cannot review their own paper.",paper=values["paper_id"],reviewer=values["reviewer_id"])
    return save_row(c,"review",values,"review_id",review_id)


def save_session(c, values, session_id):
    reject_if(c,"""SELECT 1 FROM paper p JOIN track t USING(track_id)
              WHERE p.session_id=:id AND t.conference_id<>:conference""",
              "Moving this session would invalidate a scheduled paper.",id=session_id,conference=values["conference_id"])
    return save_row(c,"conference_session",values,"session_id",session_id)


def detail(c, table, key, item_id):
    result = require(c,table,key,item_id)
    if table == "app_user":
        for role,pk,field,labels,collection in PROFILES:
            profile = rows(c,f"SELECT {field} FROM {role} WHERE {pk}=:id",id=item_id)
            result[role] = profile[0] if profile else None
            if profile:
                profile[0][collection] = [r["area_label"] for r in rows(c,
                    f"SELECT area_label FROM {labels} WHERE {pk}=:id ORDER BY area_label",id=item_id)]
    if table == "paper":
        result["authors"] = rows(c,"""SELECT author_id,author_position,is_corresponding FROM paper_author
                              WHERE paper_id=:id ORDER BY author_position""",id=item_id)
        result["versions"] = rows(c,"""SELECT version_no,file_location,uploaded_at,change_note FROM paper_version
                              WHERE paper_id=:id ORDER BY version_no DESC""",id=item_id)
        result["keywords"] = [r["keyword"] for r in rows(c,
            "SELECT keyword FROM paper_keyword WHERE paper_id=:id ORDER BY keyword",id=item_id)]
    return result


def register_resource(path, table, key, form, writer):
    def list_items():
        with engine.connect() as c:
            return rows(c,f"SELECT * FROM {table} ORDER BY {key}")

    def read_item(item_id: int):
        with engine.connect() as c:
            return detail(c,table,key,item_id)

    def create_item(body: form):
        with engine.begin() as c:
            item_id = writer(c,body.model_dump(),None)
            return detail(c,table,key,item_id)

    def update_item(item_id: int, body: form):
        with engine.begin() as c:
            require(c,table,key,item_id)
            writer(c,body.model_dump(),item_id)
            return detail(c,table,key,item_id)

    def delete_item(item_id: int):
        with engine.begin() as c:
            require(c,table,key,item_id)
            c.execute(text(f"DELETE FROM {table} WHERE {key}=:id"),{"id":item_id})
        return Response(status_code=204)

    for method, suffix, handler, status in [
        ("GET","",list_items,200),("POST","",create_item,201),
        ("GET","/{item_id}",read_item,200),("PUT","/{item_id}",update_item,200),
        ("DELETE","/{item_id}",delete_item,204)
    ]:
        app.add_api_route("/"+path+suffix,handler,methods=[method],tags=[path],
                          name=handler.__name__+"_"+path,status_code=status)


register_resource("users","app_user","user_id",User,save_user)
register_resource("papers","paper","paper_id",Paper,save_paper)
register_resource("reviews","review","review_id",Review,save_review)
register_resource("sessions","conference_session","session_id",Session,save_session)


@app.get("/reference",tags=["Reference"])
def reference():
    with engine.connect() as c:
        return {t:rows(c,f"SELECT * FROM {t} ORDER BY 1,2") for t in
                ("conference","conference_host","conference_reviewer","track","author_research_area","reviewer_expertise")}


@app.get("/schedule",tags=["Reference"])
def schedule():
    with engine.connect() as c:
        return rows(c,"""SELECT * FROM accepted_paper_schedule
                    ORDER BY conference_id,session_date,start_time,session_id,paper_id""")
