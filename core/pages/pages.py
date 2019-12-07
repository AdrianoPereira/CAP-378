from core.components import Div, Span, P
from core.components import Dropdown, RadioItems, Graph, Location, Link
from core import constants as const
from core.components import (
    build_banner,
    build_graph_title,
    build_menu,
    build_header,
    build_content,
    build_footer,
    build_download_controls
)


def build_glm_page(app):
    # page = [build_menu()]
    page = []
    page.append(build_header(app))
    page.append(build_content())
    page.append(build_footer())

    return page


def build_abi_page():
    page = [build_menu()]

    return page


def build_download_page():
    page = [build_menu()]
    page.append(build_download_controls())
    page.append(Div(id='data-download'))

    return page
