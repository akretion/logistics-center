# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2015 Sebastien BEAU @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.addons.connector.backend as backend


logistic = backend.Backend('logistic')
""" Generic Logistic Backend """

logistic_base = backend.Backend(
    parent=logistic, version='logistic_base')
""" Logistic Backend for version 0 """
