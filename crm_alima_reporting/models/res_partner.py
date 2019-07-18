# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Partner(models.Model):

    _inherit = 'res.partner'

    domaine_intervention = fields.Text(string="Domaine d'intervention")
    condition_financement = fields.Text(string="Condition de financement")
    historique = fields.Text(string="Historique")
    liens = fields.One2many('crm.alima.reporting.autresliens', 'partner', string='Autres liens')
    annexes_rapport_intermediaire = fields.Text(string="Annexes Rapport Intermediaire")
    annexes_rapport_final = fields.Text(string="Annexes Rapport Final")

    login = fields.Char(string='Login')
    pwd = fields.Char(string='Mot de passe')


class Autresliens(models.Model):
    _name = "crm.alima.reporting.autresliens"

    name = fields.Char(string="Titre")
    desccription = fields.Text(string="Description du lien")
    lien = fields.Char(string="lien")
    partner = fields.Many2one('crm.partner', string='Bailleur', required=True)

