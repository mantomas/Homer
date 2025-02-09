from datetime import datetime, time
from enum import Enum

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from markupsafe import escape

from homer import db
from homer.main import bp
from homer.models import Heating, Page, ToDo, User
from homer.main.forms import HeatingForm, PageForm, ToDoForm


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    form = ToDoForm()
    # homepage shows only active tasks
    todos = (
        db.session.execute(
            db.select(ToDo).where(ToDo.done == 0).order_by(ToDo.due_date.asc())
        )
        .scalars()
        .all()
    )
    todos = mark_tasks(todos)
    if form.validate_on_submit():
        to_flash = None
        try:
            now = datetime.now()
            author = current_user._get_current_object().id
            due_day = form.due_day.data
            due_hour = time(int(form.due_hour.data), 0, 0)
            due = datetime.combine(due_day, due_hour)
            record = ToDo(
                created=now,
                author_id=author,
                last_edit_by=author,
                last_edited=now,
                title=form.title.data,
                body=form.body.data,
                due_date=due,
                done=False,
            )
            db.session.add(record)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception:
            to_flash = TODO_ERROR
        if to_flash:
            flash(to_flash)
            return render_template(
                "index.html",
                title="Seznam úkolů",
                form=form,
                current_user=current_user,
                todos=todos,
            )
        else:
            flash(
                f"Vytvořeno: {form.title.data} | "
                f"Termín: {due.strftime('%d.%m.%Y %H')}:00"
            )
            return redirect(url_for(".index"))
    return render_template(
        "index.html",
        title="Seznam úkolů",
        form=form,
        current_user=current_user,
        todos=todos,
    )


class ToDoStatus(Enum):
    # enum mapping to Bootstrap table classes
    DONE = "table-success"
    OVERDUE = "table-danger"
    CLOSE = "table-warning"
    SAFE = "table-info"
    FAR = "table-light"


def mark_tasks(todos: list[ToDo]):
    for todo in todos:
        days_left = (todo.due_date - datetime.now()).days
        if todo.done:
            todo.table_class = ToDoStatus.DONE
        elif days_left < 0:
            todo.table_class = ToDoStatus.OVERDUE
        elif days_left < 7:
            todo.table_class = ToDoStatus.CLOSE
        elif days_left < 14:
            todo.table_class = ToDoStatus.SAFE
        else:
            todo.table_class = ToDoStatus.FAR
    return todos


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

HEATING_ERROR = "Něco se nepovedlo, zkontroluj si hodnoty."
TODO_ERROR = "Úkol musí obsahovat titulek a termín."


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


@bp.route("/heating", methods=["GET", "POST"])
def heating():
    form = HeatingForm()
    page = request.args.get("page", 1, type=int)
    records = db.paginate(
        db.select(Heating).order_by(Heating.burn_date.desc()), page=page, per_page=30
    )
    if form.validate_on_submit():
        to_flash = None
        try:
            record = Heating(
                weight=form.weight.data,
                temperature_in=form.temperature_in.data,
                temperature_out=form.temperature_out.data,
                burn_date=form.burn_date.data,
                note=form.note.data,
            )
            db.session.add(record)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception as exc:
            to_flash = exc
        if to_flash:
            flash(to_flash)
            return render_template(
                "heating.html",
                title="Záznamy o topení",
                form=form,
                current_user=current_user,
                records=records,
            )
        else:
            day = record.burn_date.strftime("%d.%m.%Y")
            flash(f"Záznam {day} uložen.")
            return redirect(url_for(".heating"))
    return render_template(
        "heating.html",
        title="Záznamy o topení",
        form=form,
        current_user=current_user,
        records=records,
    )


@bp.route("/heating/<id>/edit", methods=["GET", "POST"])
@login_required
def heating_edit(id):
    record = db.one_or_404(db.select(Heating).where(Heating.id == escape(id)))
    form = HeatingForm()
    if form.burn_date.data is None:
        burn_date = record.burn_date
    else:
        burn_date = form.burn_date.data
    title_date = burn_date.strftime("%d.%m.%Y")
    if form.validate_on_submit():
        to_flash = None
        try:
            record.weight = form.weight.data
            record.temperature_in = form.temperature_in.data
            record.temperature_out = form.temperature_out.data
            record.burn_date = form.burn_date.data
            record.note = form.note.data
            db.session.add(record)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception as exc:
            to_flash = exc
        burn_date = record.burn_date.strftime("%d.%m.%Y")
        if to_flash:
            flash(to_flash)
            return render_template(
                "heating_edit.html",
                title=f"Úprava záznamu z {title_date}",
                form=form,
                current_user=current_user,
            )
        else:
            flash(f"Záznam z {burn_date} upraven.")
            return redirect(url_for(".heating"))
    form.burn_date.data = record.burn_date
    form.weight.data = record.weight
    form.temperature_in.data = record.temperature_in
    form.temperature_out.data = record.temperature_out
    form.note.data = record.note
    return render_template(
        "heating_edit.html",
        title=f"Úprava záznamu z {title_date}",
        form=form,
        current_user=current_user,
    )


@bp.route("/heating/season/<season_id>", methods=["GET"])
def heating_season(season_id):
    season_records = (
        db.session.execute(
            db.select(Heating)
            .where(Heating.season == escape(season_id))
            .order_by(Heating.burn_date.asc())
        )
        .scalars()
        .all()
    )
    if not season_records:
        flash(f"Žádné záznamy pro topnou sezonu {escape(season_id)}.")
        return redirect(url_for(".heating"))
    season_days = (season_records[-1].burn_date - season_records[0].burn_date).days
    total_weight = sum([record.weight for record in season_records])
    temperatures_in = [record.temperature_in for record in season_records]
    temperatures_out = [record.temperature_out for record in season_records]
    # put together some stats
    statistics = {
        "total_rounds": len(season_records),
        "total_weight": total_weight,
        "avg_weight": f"{(total_weight / len(season_records)):.1f}",
        "season_start": season_records[0].burn_date.strftime("%d/%m/%Y"),
        "season_end": season_records[-1].burn_date.strftime("%d/%m/%Y"),
        "season_days": season_days,
        "average_round": f"{((season_days * 24) / len(season_records)):.0f}",
        "avg_temp_in": f"{(sum(temperatures_in) / len(season_records)):.1f}",
        "avg_temp_out": f"{(sum(temperatures_out) / len(season_records)):.1f}",
    }

    return render_template(
        "heating_season.html",
        title=f"Topná sezóna {season_id}",
        statistics=statistics,
    )


@bp.route("/todo/<id>", methods=["GET"])
def todo_view(id):
    todo = db.one_or_404(db.select(ToDo).where(ToDo.id == escape(id)))
    author = db.get_or_404(User, todo.author_id)
    if todo.last_edit_by == todo.author_id:
        editor = author
    else:
        editor = db.get_or_404(User, todo.last_edit_by)
    return render_template(
        "todo_view.html", title=todo.title, todo=todo, author=author, editor=editor
    )


@bp.route("/todo/<id>/edit", methods=["GET", "POST"])
@login_required
def todo_edit(id):
    todo = db.one_or_404(db.select(ToDo).where(ToDo.id == escape(id)))
    old_title = todo.title
    form = ToDoForm()
    if form.validate_on_submit():
        to_flash = None
        try:
            due_day = form.due_day.data
            due_hour = time(int(form.due_hour.data), 0, 0)
            due = datetime.combine(due_day, due_hour)
            todo.title = form.title.data
            todo.due_date = due
            todo.body = form.body.data
            todo.last_edit_by = current_user._get_current_object().id
            todo.last_edited = datetime.now()
            db.session.add(todo)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception:
            to_flash = TODO_ERROR
        if to_flash:
            flash(to_flash)
            return render_template(
                "todo_edit.html",
                title=f"Upravuješ: {old_title}",
                form=form,
                current_user=current_user,
            )
        else:
            flash(f"Úkol změněn: {todo.title}")
            return redirect(url_for(".todo_view", id=todo.id))
    form.title.data = todo.title
    form.body.data = todo.body
    form.due_day.data = todo.due_date.date()
    form.due_hour.data = todo.due_date.time().hour
    return render_template(
        "todo_edit.html",
        title=f"Upravuješ: {todo.title}",
        form=form,
        current_user=current_user,
    )


@bp.route("/todo/<id>/switch", methods=["GET"])
@login_required
def todo_switch(id):
    todo = db.one_or_404(db.select(ToDo).where(ToDo.id == escape(id)))
    to_flash = None
    new_status = not todo.done
    if new_status:
        done_date = datetime.now()
    else:
        done_date = None
    try:
        todo.done = new_status
        todo.done_date = done_date
        db.session.add(todo)
        db.session.commit()
    except ValueError as e:
        to_flash = str(e)
    except Exception:
        to_flash = "Něco se nepovedlo."
    if to_flash:
        flash(to_flash)
    else:
        if todo.done:
            flash(f"Hotovo: {todo.title}")
        else:
            flash(f"Zpět do práce: {todo.title}")
    return redirect(request.referrer)


@bp.route("/todo", methods=["GET", "POST"])
def todo():
    form = ToDoForm()
    # all tasks for the todo page with pagination
    page = request.args.get("page", 1, type=int)
    todos = db.paginate(
        db.select(ToDo).order_by(ToDo.id.desc()), page=page, per_page=30
    )
    todos = mark_tasks(todos)
    if form.validate_on_submit():
        to_flash = None
        try:
            now = datetime.now()
            author = current_user._get_current_object().id
            due_day = form.due_day.data
            due_hour = time(int(form.due_hour.data), 0, 0)
            due = datetime.combine(due_day, due_hour)
            record = ToDo(
                created=now,
                author_id=author,
                last_edit_by=author,
                last_edited=now,
                title=form.title.data,
                body=form.body.data,
                due_date=due,
                done=False,
            )
            db.session.add(record)
            db.session.commit()
        except ValueError as e:
            to_flash = str(e)
        except Exception:
            to_flash = TODO_ERROR
        if to_flash:
            flash(to_flash)
            return render_template(
                "todo.html",
                title="Všechny úkoly",
                form=form,
                current_user=current_user,
                todos=todos,
            )
        else:
            flash(
                f"Vytvořeno: {form.title.data} | "
                f"Termín: {due.strftime('%d.%m.%Y %H')}:00"
            )
            return redirect(url_for(".index"))
    return render_template(
        "todo.html",
        title="Všechny úkoly",
        form=form,
        current_user=current_user,
        todos=todos,
    )
