DENOMINATIONS = {
    "protestant": {
        "canon": "66 books",
        "notes": "Sola Scriptura; no deuterocanonical books",
        "distinctives": ["salvation by faith alone", "priesthood of all believers"],
    },
    "catholic": {
        "canon": "73 books (includes deuterocanonical/Apocrypha)",
        "notes": "Scripture + Tradition; Papal authority",
        "distinctives": ["purgatory", "Marian doctrines", "seven sacraments"],
    },
    "orthodox": {
        "canon": "varies (typically includes more deuterocanonical texts)",
        "notes": "Holy Tradition; Ecumenical Councils",
        "distinctives": ["theosis", "icons", "different Christological emphases"],
    },
    "evangelical": {
        "canon": "66 books",
        "notes": "Bible inerrancy, personal conversion emphasis",
        "distinctives": ["born-again experience", "missions focus"],
    },
    "non_denominational": {
        "canon": "66 books",
        "notes": "Non-creedal, Bible-focused",
        "distinctives": [],
    },
}


def get_denomination_context(denomination: str) -> str:
    info = DENOMINATIONS.get(denomination, DENOMINATIONS["protestant"])
    distinctives = ", ".join(info["distinctives"]) if info["distinctives"] else "no fixed list"
    return (
        f"{denomination.replace('_', ' ').title()} lens: canon={info['canon']}; "
        f"notes={info['notes']}; distinctives={distinctives}."
    )


def denomination_note(denomination: str) -> str:
    return get_denomination_context(denomination)


def canon_difference_note(query: str, denomination: str) -> str | None:
    terms = {"maccabees", "sirach", "wisdom of solomon", "tobit", "judith", "baruch"}
    if any(term in query.lower() for term in terms):
        return (
            "Canon note: Catholic and Orthodox traditions include deuterocanonical books "
            "that most Protestant Bibles do not. This local KJV corpus currently validates "
            "the 66-book Protestant canon, so deuterocanonical citations should be checked "
            "against an approved Catholic or Orthodox edition."
        )
    return None
