from homer.models import Page


def inject_navigation(db):
    def _inject_navigation():
        pages = sorted(
            db.session.query(Page).with_entities(Page.url_suffix).all(),
            key=lambda p: p.url_suffix,
        )
        return dict(pages=pages)

    return _inject_navigation
