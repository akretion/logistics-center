# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Logistics center",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "summary": "Common module for logistics center and external warehouse",
    "author": "Akretion",
    "license": "AGPL-3",
    "website": "https://www.akretion.com",
    "depends": ["delivery", "stock_usability"],
    "external_dependencies": {},
    "data": [
        "data/data.xml",
        "views/backend_view.xml",
        "views/stock_view.xml",
        "views/attachment_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "installable": True,
}
