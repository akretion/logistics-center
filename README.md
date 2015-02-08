odoo-logistic-center
====================

Allow to exchange file datas between Odoo ERP and external warehouses


![Logistics Connector](/connector_logistics_center/doc/logistics_connector.png "Logitics Center Connector")



Required Code
-----------------

https://github.com/akretion/file-exchange

https://github.com/akretion/connector-import-data

https://github.com/OCA/sale-workflow/tree/7.0


Quick Start
--------------

* Install bleckmann_logistics_customize module
* Menu Connectors > Logistics > Backends
* Click to create a new backend 
* Select 'Bleckmann' as Logistics Center field
* Select 'Version' and 'Warehouse' under 'Logistics configuration' and save
* Here is what you should see:


![Logistics Backend and Tasks](/connector_logistics_center/doc/logistics_task.png "Logistics Backend and Tasks")

* To send your product catalog (previously attached to this backend) to your logistics center, just click on Green right arrow.


* To attach a product to your Logistics Center, go to Product Connector tab and add it.


![Logistics product](/connector_logistics_center/doc/product_log.png "Logistics Product")




* To manage checks and alerts on Sales, customize existing Exception Rules or create others.


![Logistics Sale Rules](/connector_logistics_center/doc/rules.png "Logistics Sale Rules")

