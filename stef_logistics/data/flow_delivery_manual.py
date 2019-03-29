
portal_delivery_head = [
{'seq': 1, 'type': 'A', 'col': 'del_ord', 'req': True, 'comment': "Delivery Order number"},
{'seq': 2, 'type': 'A', 'col': 'cmdcli', 'req': False, 'comment': "N° de référence donneur d'ordre: cmde d'origine"},
{'seq': 3, 'type': 'A', 'col': 'trsdst', 'req': True, 'comment': "Code du tiers destinataire à livrer"},
{'seq': 4, 'type': 'D5', 'col': 'datliv', 'req': True, 'comment': "Date livr"},
{'seq': 4, 'type': 'D5', 'col': 'dat_drop', 'req': True, 'comment': "Date destination"},
]


portal_delivery_line = [
{'seq': 1, 'len': 16, 'type': 'A', 'col': 'codprd', 'req': True, 'comment': "alias produit"},
{'seq': 2, 'len': 2, 'type': 'A', 'col': 'type_ul', 'req': True, 'comment': "type ul"},
{'seq': 3, 'len': 20, 'type': 'A', 'col': 'num_lot', 'req': False, 'comment': "réf lot"},
{'seq': 4, 'len': 6, 'type': 'I', 'col': 'qty', 'req': True, 'comment': "qté"},
{'seq': 5, 'type': 'I', 'col': 'weight', 'req': True, 'comment': "poids"},
{'seq': 6, 'type': 'D5', 'col': 'rotation', 'req': False, 'comment': "date rotation"},
{'seq': 7, 'type': 'A', 'col': 'palette', 'req': False, 'comment': "référence palette client"},
]
