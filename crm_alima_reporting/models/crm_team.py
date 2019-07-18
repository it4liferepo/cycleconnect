# -*- coding: utf-8 -*-

from odoo import api, fields, models




class CrmTeam(models.Model):
    _inherit="crm.team"
    _description= 'Team'

    manager_mail = fields.Text('Mail Manager')
