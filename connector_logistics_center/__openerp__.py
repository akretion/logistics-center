# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Connector logistics center',
    'version': '0.8',
    'category': 'Warehouse',
    'sequence': 10,
    'summary': "Common module for logistics center and external warehouse",
    'description': """
Connector logistics center
==========================

Description
-----------

Common module for logistics center and external warehouse management
with csv file

Export :

- catalog
- products to receive
- products to deliver

Import :

- catalog inventory
- received products
- sent products


Implementation example
----------------------
see Bleckmann Logistics module in the same branch



    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale_stock',
        'sale_exceptions',
        'purchase',
        'connector_base_product',
        'connector_buffer',
        'file_repository',
    ],
    'external_dependencies': {
        'Python': ['unicodecsv'],
    },
    'data': [
        'backend_view.xml',
        'logistic_view.xml',
        'stock_view.xml',
        'sale_view.xml',
        'purchase_view.xml',
        'file_exchange_view.xml',
        'data/sale_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [
    ],
    'css': [
    ],
    'js': [
    ],
    'qweb': [
    ],
}
