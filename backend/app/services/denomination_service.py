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

DENOMINATION_CONTEXTS = {
    "protestant": (
        "You are responding from a Protestant perspective. Key distinctives: "
        "Sola Scriptura (Scripture alone as authority), salvation by faith alone, "
        "66-book canon. Do not mention purgatory or deuterocanonical texts. "
        "Do not expose internal metadata."
    ),
    "catholic": (
        "You are responding from a Catholic perspective. Key distinctives: "
        "Scripture and Tradition as co-equal authority, 73-book canon including "
        "deuterocanonical texts, belief in purgatory and seven sacraments. "
        "Do not expose internal metadata."
    ),
    "orthodox": (
        "You are responding from an Eastern Orthodox perspective. Key distinctives: "
        "Holy Tradition and Scripture, theosis (union with God), icons, Ecumenical "
        "Councils as doctrinal authority. Do not expose internal metadata."
    ),
    "evangelical": (
        "You are responding from an Evangelical perspective. Key distinctives: "
        "biblical inerrancy, necessity of personal born-again conversion experience, "
        "strong missions focus, salvation through personal acceptance of Jesus. "
        "Do not expose internal metadata."
    ),
    "non_denominational": (
        "You are responding from a Non-denominational perspective. Provide a purely "
        "scripture-grounded answer with no tradition-specific doctrinal framing. Do not "
        "reference creeds, councils, or denomination-specific practices. Do not expose "
        "internal metadata."
    ),
}

DENOMINATION_NOTES = {
    "protestant": (
        "Protestant perspective: emphasizes Scripture as the final authority, "
        "salvation by faith alone, and the 66-book canon."
    ),
    "catholic": (
        "Catholic perspective: reads Scripture with Sacred Tradition, recognizes the "
        "73-book canon, and includes sacramental and purgatory teachings where relevant."
    ),
    "orthodox": (
        "Eastern Orthodox perspective: reads Scripture within Holy Tradition, emphasizing "
        "theosis, icons, and the Ecumenical Councils."
    ),
    "evangelical": (
        "Evangelical perspective: emphasizes biblical authority, personal born-again "
        "conversion, missions, and assurance through personal faith in Jesus."
    ),
    "non_denominational": (
        "Bible-focused perspective: keeps the answer grounded in the cited passages "
        "without extra framing."
    ),
}


def get_denomination_context(denomination: str) -> str:
    return DENOMINATION_CONTEXTS.get(denomination, DENOMINATION_CONTEXTS["protestant"])


def denomination_note(denomination: str) -> str:
    return DENOMINATION_NOTES.get(denomination, DENOMINATION_NOTES["protestant"])


def denomination_label(denomination: str) -> str:
    labels = {
        "protestant": "Protestant",
        "catholic": "Catholic",
        "orthodox": "Eastern Orthodox",
        "evangelical": "Evangelical",
        "non_denominational": "Non-denominational",
    }
    return labels.get(denomination, labels["protestant"])


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
