from datetime import datetime

from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from markupsafe import escape

from homer import db
from homer.main import bp
from homer.models import Page, User
from homer.main.forms import PageForm


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/status")
@login_required
def status():
    return render_template("health.html", title="Status", current_user=current_user)


@bp.route("/page/<url_suffix>")
def page_read(url_suffix):
    page = db.one_or_404(db.select(Page).where(Page.url_suffix == escape(url_suffix)))
    author = db.get_or_404(User, page.author_id)
    if page.last_edit_by == page.author_id:
        editor = author
    else:
        editor = db.get_or_404(User, page.last_edit_by)
    return render_template(
        "page_view.html", title=page.title, page=page, author=author, editor=editor
    )


PAGE_ERROR = (
    "Něco se nepovedlo: URL část musí být unikátní..., "
    "ale možná se ti povedla úplně nová neznámá chyba. "
    "Zkoušej dál, have fun."
)


@bp.route("/page", methods=["GET", "POST"])
def page():
    form = PageForm()
    if form.validate_on_submit():
        to_flash = None
        try:
            page = Page(
                title=form.title.data,
                url_suffix=form.url_suffix.data,
                body=form.body.data,
                author_id=current_user._get_current_object().id,
                last_edit_by=current_user._get_current_object().id,
            )
            db.session.add(page)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception:
            to_flash = PAGE_ERROR
        if to_flash:
            flash(to_flash)
            return render_template(
                "page.html", title="Nová stránka", form=form, current_user=current_user
            )
        else:
            flash("Stránka byla vytvořena.")
            return redirect(url_for(".page_read", url_suffix=page.url_suffix))
    return render_template(
        "page.html", title="Nová stránka", form=form, current_user=current_user
    )


@bp.route("/page/<url_suffix>/edit", methods=["GET", "POST"])
@login_required
def page_edit(url_suffix):
    page = db.one_or_404(db.select(Page).where(Page.url_suffix == escape(url_suffix)))
    old_title = page.title
    form = PageForm()
    if form.validate_on_submit():
        to_flash = None
        try:
            page.title = form.title.data
            page.url_suffix = form.url_suffix.data
            page.body = form.body.data
            page.last_edit_by = current_user._get_current_object().id
            page.last_edited = datetime.now()
            db.session.add(page)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception:
            to_flash = PAGE_ERROR
        if to_flash:
            flash(to_flash)
            return render_template(
                "page.html",
                title=f"Upravuješ: {old_title}",
                form=form,
                current_user=current_user,
            )
        else:
            flash("Stránka byla změněna.")
            return redirect(url_for(".page_read", url_suffix=page.url_suffix))
    form.title.data = page.title
    form.url_suffix.data = page.url_suffix
    form.body.data = page.body
    return render_template(
        "page.html",
        title=f"Upravuješ: {page.title}",
        form=form,
        current_user=current_user,
    )
