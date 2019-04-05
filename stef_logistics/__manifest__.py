# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stef logistics center',
    'version': '12.0.0.0.0',
    'category': 'Warehouse',
    'summary': "Stef logistics center",
    'description': """
Stef logistics center
=====================

Description
-----------

Stef Logistics exchange management :

Export :

- products to receive
- products to deliver

Import :

- not implemented

Settings
--------

    * Define an new warehouse for your logistics center
    * Create a new Logistic backend (menu connector/logistics/backend)
      by selecting the existing 'file repository' ('Stef')
    * Select the created warehouse in this logistics center and
      set a version or create a new one (see module Stef_logistics_customize)
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
        'stock',
        'logistics_center',
    ],
    'external_dependencies': {
        'Python': [
        ],
    },
    'data': [
        'data/delivery_data.xml',
        'data/warehouse_data.xml',
        'data/logistics_flow_data.xml',
        'views/partner_view.xml',
        # 'data/sale_data.xml',
        # 'data/repository_data.xml',
        # 'data/repository.task.csv',
        # 'data/backend_data.xml',
        # 'data/cron_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
