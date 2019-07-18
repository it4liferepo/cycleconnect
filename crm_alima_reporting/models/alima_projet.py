# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

# ---------------------------------------------------------
# Projet
# ---------------------------------------------------------
class Alima_projet(models.Model):
    _name = "crm.alima.reporting.projet"
    _description = "projet de Alima"
    _order = "name"

    code_projet = fields.Char('Code projet', required=True)
    name = fields.Char('Description projet', translate=True)
    debut = fields.Date('Date de début')
    fin = fields.Date('Date de fin')
    localite = fields.Char('Localité')
    mission_id = fields.Many2one('crm.alima.reporting.mission', string='Mission', required=True)

    _sql_constraints = [
        ('uniq_name', 'unique(name)', "A project already exists with this name . Project's name must be unique!"),
        ('uniq_code', 'unique(code_projet)', "A project's code already exists with this code . Project's code must be unique!"),
    ]