# -*- coding: utf-8 -*-

from odoo import fields, models, tools

from ..models import crm_alima_don
class CrmAlimaReports(models.Model):
    """ CRM Dons Analysis """
    #row_number() over () as id, pour ajouter un id sur la requete
    _name = "crm.alima.dashboard.un"
    _auto = False
    _description = "Repartition annuelle des dons"
    _rec_name = 'annee'

    annee = fields.Char(string='Annee', readonly=True)
    montant = fields.Float('Total dons prive', readonly=True,  digits=(16, 2), group_operator="sum", help="Total dons prive")
    nombre = fields.Float('Nombre de dons', readonly=True,  digits=(16, 0), group_operator="sum", help="Nombre de dons")
    moyen = fields.Float('Dons moyens', readonly=True,  digits=(16, 2), group_operator="avg", help="Dons moyenss")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_alima_dashboard_un')
        self._cr.execute("""
            CREATE VIEW crm_alima_dashboard_un AS (
                SELECT
                    c.id,
                    date_part('year', c.date) as annee,
                    sum(c."montantEur") as montant,
                    count(c."montantEur") as nombre,
                    avg(c."montantEur") as moyen
                FROM
                    public.crm_alima_don c
                GROUP BY
                    annee, c.id
            )""")
class CrmAlimaReportsDeux(models.Model):
    """ CRM Dons Analysis """
    _name = "crm.alima.dashboard.deux"
    _auto = False
    _description = "Montant collectés par type donnateur"
    _rec_name = 'type'

    type = fields.Char(string='Type', readonly=True)
    anneedonateur = fields.Char(string='Annee premier don', readonly=True)
    annedon = fields.Char(string='Date du don', readonly=True)
    mode_versement = fields.Char(string='Mode de versement', readonly=True)
    type_de_personne = fields.Char(string='type de personne', readonly=True)
    nombre = fields.Float('Nombre de dons', readonly=True,  digits=(16, 0), group_operator="sum", help="Nombre de dons")
    montant = fields.Float('Montant dons Euro', readonly=True,  digits=(16, 2), group_operator="sum", help="Total dons euro")
    id = fields.Char(string='donateur', readonly=True)


    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_alima_dashboard_deux')
        self._cr.execute("""
            CREATE VIEW crm_alima_dashboard_deux AS (
                SELECT
                    public.crm_alima_donateur.id as id,
                    1 as nombre,
                    public.crm_alima_don."montantEur" as montant,
                    date_part('year', crm_alima_donateur."datePremierDon") as anneedonateur,
                    date_part('year', crm_alima_don."date") as annedon,
                    (CASE WHEN date_part('year', crm_alima_don."date") = date_part('year', crm_alima_donateur."datePremierDon")
                    THEN 'nouveaux donateurs' ELSE 'anciens donateurs' END) as type,
                    crm_alima_don.mode_versement,
                    crm_alima_donateur.type_de_personne
                FROM
                    public.crm_alima_don,
                    public.crm_alima_donateur
                where
                    public.crm_alima_donateur.id = public.crm_alima_don.donateur
                ORDER BY
                    date_part('year', crm_alima_don."date")
            )""")
