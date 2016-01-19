# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Multicompany logistics center',
    'version': '0.8',
    'category': 'Warehouse',
    'sequence': 10,
    'summary': "Multicompany backend logistics center ",
    'description': """
Multicompany logistics center
==============================

Description
-----------

Allow to use the same logistics backend for several companies.
Backend warehouse field becomes a property field.

    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'connector_logistics_center',
    ],
    'external_dependencies': {
        'Python': [],
    },
    'data': [
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
