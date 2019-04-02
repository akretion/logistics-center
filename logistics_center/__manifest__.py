# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Logistics center',
    'version': '12.0.0.0.1',
    'category': 'Warehouse',
    'summary': "Common module for logistics center and external warehouse",
    'description': """
Connector logistics center
==========================

Description
-----------

Common module for logistics center and external warehouse management
with csv file

Export :

- products to receive
- products to deliver

Import :

- received products
- sent products


    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'delivery',
        'stock_usability',
    ],
    'external_dependencies': {
    },
    'data': [
        'data/data.xml',
        'views/backend_view.xml',
        'views/stock_view.xml',
        'views/attachment_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'images': [
    ],
}
