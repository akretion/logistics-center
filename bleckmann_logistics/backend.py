# -*- coding: utf-8 -*-

import openerp.addons.connector.backend as backend
import openerp.addons.connector_logistics_center.backend as logistic_backend
from .output import BACKEND_VERSION


logistic_bleckmann = backend.Backend(
    parent=logistic_backend.logistic_base, version=BACKEND_VERSION)
