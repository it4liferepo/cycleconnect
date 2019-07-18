# -*- coding: utf-8 -*-
import requests
from datetime import datetime, date

from odoo import models, api, fields, _

class Requests(models.Model):
    _name = 'crm.requests'
    _description = 'Requests'

    nbre_donateurs = fields.Integer(store=True)
    nbre_dons = fields.Integer(store=True)
    date = fields.Date(store=True)

    @api.multi
    def check_campagne_exist(self,identifiant):
        return True if self.env['crm.alima.code.media'].search([('identifiant', '=', identifiant)]) else False

    @api.multi
    def check_donateur_exist(self,email):
        return True if self.env['crm.alima.donateur'].search([('name', '=', email)]) else False



    @api.multi
    def scheluder_crm_hello_asso(self):
        username = 'solthis'
        password = 'NKeBmPqiJ4U3yYmQNvHca'
        organism_id = '000000363791'

        uri = 'https://api.helloasso.com/v3'
        endpoint_campaign = '/organizations/'+organism_id+'/campaigns.json'
        endpoint_action = '/organizations/'+organism_id+'/actions.json?page=1&results_per_page=100'

        #Campagn
        r_campaign = requests.get(uri+endpoint_campaign, auth = (username, password))
        if r_campaign.status_code == 200:
            #Success
            data = r_campaign.json()['resources']
            for campaign in data:
                if not self.check_campagne_exist(campaign['id']):
                    self.env['crm.alima.code.media'].create({
                        'identifiant': campaign['id'],
                        'url': campaign['url'],
                        'name': campaign['name'],
                        'nomcampagne': campaign['name'],
                        'annees': campaign['creation_date'],
                    })

        #Donateurs et dons
        r_action = requests.get(uri+endpoint_action, auth = (username, password))
        if r_action.status_code == 200:
            #Success
            data = r_action.json()['resources']
            for donateur in data:
                if 'email' in donateur and not self.check_donateur_exist(donateur['email']):
                    self.env['crm.alima.donateur'].create({
                        'lastname': donateur['last_name'] if 'last_name' in donateur else False,
                        'firstname': donateur['first_name'] if 'first_name' in donateur else False,
                        'email': donateur['email'],
                        'codepostale': donateur['zip_code'] if 'zip_code' in donateur else False ,
                        'country_id': donateur['country'] if 'country' in donateur else False,
                        'complementnom': donateur['address'] if 'address' in donateur else False,
                        'est_donateur': True,
                    })
            for don in data:
                if 'email' in don and don['status'] == 'PROCESSED':
                    id_donateur = self.env['crm.alima.donateur'].search([('name', '=', don['email'])], limit=1).id
                    id_code_Media = self.env['crm.alima.code.media'].search([('identifiant', '=', don['id_campaign'])], limit=1).id
                    self.env['crm.alima.don'].create({
                        'donateur': id_donateur,
                        'codeMedia': id_code_Media,
                        'date': don['date'].split('T')[0] if 'date' in don else False,
                        'montantEur': float(don['amount']) if 'amount' in don else False,
                        'mode_versement': 'sans prelevement',
                        'hello_asso': True,
                    })



    @api.multi
    def scheluder_crm_hello_asso_by_days(self):
        username = 'solthis'
        password = 'NKeBmPqiJ4U3yYmQNvHca'
        organism_id = '000000363791'
        today = str(datetime.today().date())
        today = '2019-04-10' #test à enlever
        date_from = today+'T'+'00:00:00'
        date_to = today+'T'+'23:59:59'

        uri = 'https://api.helloasso.com/v3'
        endpoint_campaign = '/organizations/'+organism_id+'/campaigns.json'
        endpoint_action = '/organizations/'+organism_id+'/actions.json?page=1&results_per_page=100'+'&'+'from='+date_from+'&'+'to='+date_to

        nbre_donateurs=nbre_dons=0


        #Campagn
        r_campaign = requests.get(uri+endpoint_campaign, auth = (username, password))
        if r_campaign.status_code == 200:
            #Success
            data = r_campaign.json()['resources']
            for campaign in data:
                if not self.check_campagne_exist(campaign['id']):
                    self.env['crm.alima.code.media'].create({
                        'identifiant': campaign['id'],
                        'url': campaign['url'],
                        'name': campaign['name'],
                        'nomcampagne': campaign['name'],
                        'annees': campaign['creation_date'],
                    })

        #Donateurs et dons
        r_action = requests.get(uri+endpoint_action, auth = (username, password))
        if r_action.status_code == 200:
            #Success
            data = r_action.json()['resources']
            for donateur in data:
                if 'email' in donateur and not self.check_donateur_exist(donateur['email']):
                    self.env['crm.alima.donateur'].create({
                        'lastname': donateur['last_name'] if 'last_name' in donateur else False,
                        'firstname': donateur['first_name'] if 'first_name' in donateur else False,
                        'email': donateur['email'],
                        'codepostale': donateur['zip_code'] if 'zip_code' in donateur else False ,
                        'country_id': donateur['country'] if 'country' in donateur else False,
                        'complementnom': donateur['address'] if 'address' in donateur else False,
                        'est_donateur': True,
                    })
                    nbre_donateurs += 1
            for don in data:
                if 'email' in don and don['status'] == 'PROCESSED':
                    id_donateur = self.env['crm.alima.donateur'].search([('name', '=', don['email'])], limit=1).id
                    id_code_Media = self.env['crm.alima.code.media'].search([('identifiant', '=', don['id_campaign'])], limit=1).id
                    self.env['crm.alima.don'].create({
                        'donateur': id_donateur,
                        'codeMedia': id_code_Media,
                        'date': don['date'].split('T')[0] if 'date' in don else False,
                        'montantEur': float(don['amount']) if 'amount' in don else False,
                        'mode_versement': 'sans prelevement',
                        'hello_asso': True,
                    })
                    nbre_dons += 1



        if nbre_donateurs or nbre_dons:
            res = self.env['crm.requests'].sudo().create({
                'nbre_donateurs': nbre_donateurs,
                'nbre_dons': nbre_dons,
                'date': today,
            })
            template = self.env.ref('crm_solthis.email_template_edi_helloasso')
            self.env['mail.template'].browse(template.id).sudo().send_mail(res.id, force_send=True)
        else:
            res = self.env['crm.requests'].sudo().create({
                'nbre_donateurs': 0,
                'nbre_dons': 0,
                'date': today,
            })
            #template = self.env.ref('crm_solthis.email_template_edi_helloasso_none')
            #self.env['mail.template'].browse(template.id).sudo().send_mail(res.id, force_send=True)