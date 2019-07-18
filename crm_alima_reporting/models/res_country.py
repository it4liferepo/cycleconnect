# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCountry(models.Model):
    _inherit="res.country"
    
    agent_mails = fields.Text(string='Mail agent', help='Les emails sont séparés par des virgules')
    manager_mail = fields.Char(string='Mail manager')
    financier_mail = fields.Char(string='Mail financier')
