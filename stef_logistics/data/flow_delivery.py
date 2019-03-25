
delivery_head = [
{'seq': 1, 'len': 5, 'type': 'A', 'col': 'codenr', 'req': True, 'def': 'E', 'allowed': ['E'], 'comment': "Code enregistrement"},
{'seq': 2, 'len': 20, 'type': 'A', 'col': 'cmdcli', 'req': True, 'comment': "N° de référence donneur d'ordre"},
{'seq': 3, 'len': 10, 'type': 'A', 'col': 'nomdos', 'req': True, 'comment': "Nom du dossier"},
{'seq': 4, 'len': 13, 'type': 'I', 'col': 'codgln', 'req': True, 'comment': "Code GLN (EAN/UCC-13) du site STEF-TFE"},
{'seq': 6, 'len': 8, 'type': 'D1', 'col': 'datliv', 'req': True, 'comment': "Date livr"},
{'seq': 7, 'len': 16, 'type': 'A', 'col': 'trsdst', 'req': True, 'comment': "Code du tiers destinataire à livrer"},
    ]


delivery_line = [
{'seq': 1, 'len': 5, 'type': 'A', 'col': 'codenr', 'req': True, 'def': 'L', 'allowed': ['L'], 'comment': "Code du tiers destinataire à livrer"},
{'seq': 2, 'len': 20, 'type': 'A', 'col': 'cmdcli', 'req': True, 'comment': "N° de référence donneur d'ordre"},
{'seq': 3, 'len': 6, 'type': 'I', 'col': 'numlig', 'req': True, 'comment': "N° de ligne"},
{'seq': 4, 'len': 16, 'type': 'A', 'col': 'codprd', 'req': True, 'comment': "Code produit"},
{'seq': 6, 'len': 6, 'type': 'I', 'col': 'qliuc', 'req': False, 'comment': "Qté en UC"},
    ]
