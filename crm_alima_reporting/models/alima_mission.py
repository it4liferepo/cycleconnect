# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

# ---------------------------------------------------------
# Mission
# ---------------------------------------------------------
class Alima_mission(models.Model):
    _name = "crm.alima.reporting.mission"
    _description = "mission de Alima"
    _order = "name"

    code_mission = fields.Char('Code mission', required=True)
    name = fields.Char('Intitulé mission', required=True, translate=True)
    country_id = fields.Many2one('res.country', string='Pays')
    context_pays = fields.Text(string="contexte du pays")
    budget = fields.Float(string="Budget annuel mission")
    rh = fields.Text(string="RH")
    projets = fields.One2many('crm.alima.reporting.projet', 'mission_id', string='Projets')


    _sql_constraints = [
        ('uniq_name', 'unique(name)', "A mission already exists with this name . Mission's name must be unique!"),
        ('uniq_code', 'unique(code_mission)', "A mission's code already exists with this code . Mission's code must be unique!"),
    ]
