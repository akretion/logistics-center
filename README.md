odoo-logistic-center
====================

Allow to exchange file datas between Odoo ERP and external warehouses


![Logistics Connector](/connector_logistic_center/doc/logistics_connector.png "Logitics Center Connector")



Required Code
---------------

https://github.com/akretion/file-exchange

https://code.launchpad.net/~akretion-team/+junk/poc-import-data


Change module name
-------------------
update ir_module_module set name = 'connector_logistics_center' where name = 'connector_logistic_center';

update ir_module_module_dependency set name = 'connector_logistics_center' where name = 'connector_logistic_center';

update ir_model_data set module = 'connector_logistics_center' where module = 'connector_logistic_center';


idem for theses modules:

* bleckmann_logistics
* bleckmann_logistics_customize
* logistics_center_dev

