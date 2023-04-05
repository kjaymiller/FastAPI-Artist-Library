from typing import Optional, List
import pathlib
import os
import typer
import discogs_client
from tinydb import TinyDB
import dotenv
import httpx

app = typer.Typer()
dotenv.load_dotenv()

user_token = os.environ.get("DISCOGS_TOKEN")
d = discogs_client.Client("FastAPI-ArtistExplorer", user_token=user_token)
db = TinyDB("data/data.json", sort_keys=True, indent=4, separators=(",", ": "))

def get_artist(artist_name):
    """Get artist from discogs"""
    artist = d.search(artist_name, type="artist")[0]
    return httpx.get(
        f"https://api.discogs.com/artists/{artist.id}?token={user_token}"
    ).json()


def add_artist(artist_name):
    """Add artist to database"""
    artist = get_artist(artist_name)
    db = TinyDB("data/data.json", sort_keys=True, indent=4, separators=(",", ": "))
    db.insert(artist)


@app.command()
def add_artists(
    artists: Optional[List[str]] = typer.Argument(None), # noqa: B008
    artist_list: Optional[pathlib.Path] = typer.Option(None, '--file', '-f'),  # noqa: B008
):
    """Add artist to database"""
    if not any([artist_list, artists]):
        raise typer.BadParameter(
            "Please provide an artist name or a file with artist names"
        )
    if artist_list:
        for artist in artist_list.read_text().splitlines():
            add_artist(artist)

    for artist in artists:
        add_artist(artist)

    print("Done! :sun_with_face:")


if __name__ == "__main__":
    app()
