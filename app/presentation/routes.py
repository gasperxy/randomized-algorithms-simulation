from flask import Blueprint, abort, render_template, request

from ..modules import get_module_metadata, list_modules

pages_bp = Blueprint("pages", __name__, template_folder="templates")


@pages_bp.app_context_processor
def inject_modules():
    return {"registered_modules": list_modules()}


@pages_bp.route("/")
def home():
    modules = list_modules()
    markov_modules = [module for module in modules if module.slug.startswith("markov_")]
    return render_template("home.html", modules=modules, markov_modules=markov_modules)


@pages_bp.route("/experiments/<slug>", methods=["GET", "POST"])
def experiment(slug: str):
    metadata = get_module_metadata(slug)
    if metadata is None:
        abort(404)

    default_params = metadata.controller.default_parameters()
    form_data = request.form if request.method == "POST" else default_params
    result = metadata.controller.run_module(form_data, metadata.accent_color)

    return render_template(
        metadata.template_name,
        module=metadata,
        result=result,
    )
