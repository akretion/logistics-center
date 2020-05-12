# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stef logistics center",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "summary": "Stef logistics center",
    "author": "Akretion",
    "license": "AGPL-3",
    "website": "https://www.akretion.com",
    "depends": ["stock", "logistics_center"],
    "external_dependencies": {"Python": []},
    "data": [
        "data/delivery_data.xml",
        "data/warehouse_data.xml",
        "data/logistics_flow_data.xml",
        "views/partner_view.xml",
        # 'data/sale_data.xml',
        # 'data/repository_data.xml',
        # 'data/repository.task.csv',
        # 'data/backend_data.xml',
        # 'data/cron_data.xml',
    ],
    "demo": [],
    "installable": True,
}
