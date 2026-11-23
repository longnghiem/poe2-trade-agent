from sqlmodel import Session

from app.models import Mod


def test_mod_saved_and_loaded_keeps_values(db: Session) -> None:
    db.add(
        Mod(id="explicit.stat_3299347043", text="# to maximum Life", source="explicit")
    )
    db.commit()

    mod = db.get(Mod, "explicit.stat_3299347043")

    assert mod is not None
    assert mod.text == "# to maximum Life"
    assert mod.source == "explicit"
