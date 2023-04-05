import re
from typing import Annotated

from fastapi import APIRouter, Form, Request
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import BaseModel

from app.config import Settings
import app.crud as crud
from tinydb import TinyDB, Query

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)

router = APIRouter()

db = TinyDB("data/data.json", sort_keys=True, indent=4, separators=(",", ": "))
artist = Query()

class Search(BaseModel):
    search: str | None = None


@router.get("/")
def index(request: Request):
    """Home page - generates an image and name of a random artist."""

    random_artist = crud.get_random_item(db)
    artist_count = len(db.all())

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "artist_count": artist_count,
            "random_artist": random_artist,
        },
    )


@router.get("/about")
def about(request: Request):
    """About page - some background information about this app."""

    return templates.TemplateResponse("about.html", {"request": request})

def get_members(artist: dict):
    """This returns active members from the artist_details table. This
    method can be used within the Jinja template."""

    if "members" not in artist:
        return [artist["name"]]
    all_members = artist["members"]
    active_members = []
    for member in all_members:
        if member["active"]:
            active_members.append(member["name"])
    return active_members  # limit 14 members

def get_website(artist: dict):
    if urls:=(artist.get("urls", artist.get("uri", []))):
        return urls[0]
    else:
        return "No website available"

def get_profile(artist: dict):
    if not (profile:=artist.get("profile", None)):
        return "No profile available"
    else:
        profile = artist["profile"]
        profile = profile.replace("[", "<").replace("]", ">")
        return profile

@router.get("/catalog")
def catalog(request: Request):
    """Catalog page - display information about artists in database."""

    artists = db.all()

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "artists": artists,
            "get_website": get_website,
        },
    )


@router.get("/profile")
def profile(request: Request):
    """Profile page - display information about a specific artist."""
    if request.headers.get("hx-request"):
        request.headers.get("HX-Trigger")
        artist = db.get(doc_id=int(request.headers.get("HX-Trigger")))
        return templates.TemplateResponse(
            "artist/profile.html",
            {
                "request": request,
                "artist": artist,
                "get_website": get_website,
                "get_members": get_members,
                "get_profile": get_profile,
            },
        )


@router.get("/search")
def search(request: Request):
    """Search page - display information about artists in database."""
    block_name = None
    if request.headers.get("hx-request"):
        block_name = "content"
    results = []

    return templates.TemplateResponse(
        "search.html", {"request": request, "results": results}, block_name=block_name
    )


@router.post("/search")
def search_post(request: Request, search: Annotated[str, Form()]):

    block_name = None
    if request.headers.get("hx-request"):
        block_name = "artist_card"

    # block_name = "artist_card"
    results = []
    artists = db.search(artist.name.search(f".*{search}.*", flags=re.IGNORECASE))

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "results": results,
            "artists": artists,
            "get_website": get_website,
            "get_members": get_members,
        },
        block_name=block_name,
    )
