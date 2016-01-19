# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Bleckmann logistics center',
    'version': '0.7',
    'category': 'Warehouse',
    'sequence': 10,
    'summary': "Bleckmann logistics center",
    'description': """
Bleckmann logistics center
===========================

Description
-----------

Bleckmann Logistics exchange management :

Export :

- catalog
- products to receive
- products to deliver

Import :

- catalog inventory
- received products
- sent products

Settings
--------

    * Define an new warehouse for your logistics center
    * Create a new Logistic backend (menu connector/logistic/backend)
      by selecting the existing 'file repository' ('Bleckmann')
    * Select the created warehouse in this logistics center and
      set a version or create a new one (see module bleckmann_logistics_customize)
    * Add one cron for each input task in the backend
    * You may add several crons in one click to have multiple executions
      per input task.

How to use
----------

    *

    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale_stock',
        'connector_logistics_center',
        'product_immutable_default_code',
    ],
    'external_dependencies': {
        'Python': [
            'unicodecsv',
            'pycountry',
        ],
    },
    'data': [
        'data/sale_data.xml',
        'data/repository_data.xml',
        'data/repository.task.csv',
        'data/backend_data.xml',
        'data/cron_data.xml',
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
