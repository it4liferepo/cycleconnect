# -*- coding: utf-8 -*-
from datetime import datetime, date
#from dateutil.relativedelta import relativedelta, timedelta,

from odoo import api, fields, models, tools, SUPERUSER_ID

COFINANCEMENT=[
    ('OUI','OUI'),
    ('NON','NON'),
    ('NDNSP','N/D - NSP')
]
TYPERAPORT=[
    ('Rapports Narratifs','Rapports Narratifs'),
    ('Rapports Financiers','Rapports Financiers'),
    ('Rapports Narratifs et Financiers','Rapports Narratifs et Financiers'),
    ('Autre','Autre'),
]
ETAPERAPPORT=[
    ('En attente de reception','En attente de reception'),
    ('En cours de relecture Desk/BDF','En cours de relecture Desk/BDF'),
    ('Rapport en attente de retour terrain','Rapport en attente de retour terrain'),
    ('Rapport a soumettre','Rapport à soumettre')
]
OUINON=[
    ('OUI','OUI'),
    ('NON','NON')
]
VALIDATION=[
    ('valide','valide'),
    ('non valide','non valide')
]

NOMRAPPORT=[
    ('Intermediaire','Intermediaire'),
    ('Final','Final'),
    ('Autre','Autre')
]
LANGUE=[
    ('Anglais','Anglais'),
    ('Francais','Français'),
]
TYPEVERSEMENT=[
    ('Local','Local'),
    ('International','International'),
]

class CrmLeadReporting(models.Model):
    _inherit="crm.lead"
    _description= 'Contrat'

    titre_complet = fields.Text('Titre complet')
    code_contrat=fields.Char(String='Code')
    pays = fields.Many2many('res.country', 'crm_lead_pays_rel', 'lead_id', 'pays_id', string='Pays du contrat', help="Liste des pays")
    projet = fields.Many2many('crm.alima.reporting.projet', 'crm_lead_projet_rel', 'lead_id', 'projet_id', string='Projets', help="Liste des projets")
    cofinancement= fields.Selection(COFINANCEMENT, string='Cofinancement', store=True)
    visibilite_terrain=state = fields.Selection(string="Visibité terrain", selection=[('OUI', 'OUI'), ('NON', 'NON'), ], required=False, )
    commentaire_visibilite_terrain=fields.Text('Commentaire visibilité')
    recherche_etude=fields.Selection(string="Recherche Etude", selection=[('OUI', 'OUI'), ('NON', 'NON'), ], required=False, )
    audit = fields.Selection(string="Audit", selection=[('OUI', 'OUI'), ('NON', 'NON'), ], required=False, )
    commentaire_audit=fields.Text(string='Commentaire audit')
    devise = fields.Many2one('res.currency', string='Devise')
    montant_bailleur=fields.Float(string='Montant bailleur')
    pourcentage_montant_bailleur= fields.Float(string='Pourcentage montant bailleur', compute='compture_pourcentage_montant_bailleur', store=True)
    montant_cofinancement= fields.Float(string='montant de cofinancement', compute='compture_montant_cofinancement', store=True)
    pourcentage_cofinancement_acquis=fields.Float(string='pourcentage de cofinancement acquis')
    couts_directs=fields.Float(string='Couts directs alima')
    couts_indirects=fields.Float(string='Couts indirects alima')
    pour_couts_indirects=fields.Float(String='Pourcentage de couts indirects alima', compute='compute_pour_couts_indirects')
    date_debut=fields.Date(string='date debut')
    date_fin=fields.Date(string='date fin')
    duree_mois=fields.Float(string='Duree en mois')
    date_signature=fields.Date(string='date de signature')
    ref_convention=fields.Char(string='réference de convention')
    signataire_alima=fields.Char(string='signataire alima')
    personne_contact_bailleur=fields.Char(string='Personne contact bailleur')
    porteur=fields.Boolean(string='Porteur')
    nomporteur=fields.Char('Nom du porteur')
    partporteur=fields.Float('Part du porteur sur le contrat')
    porteur_mou_signe= fields.Selection(string='Mou signé', selection=[('OUI','OUI'),('NON','NON')], required=False, )
    com_port_mou_signe= fields.Text(string='commentaire porteur mou signe')
    partenairelocal=fields.Boolean(string='Partenaire local')
    nompartenairelocal=fields.Char(string='Nom du partenaire local')
    partenaire_mou_signe= fields.Selection(string='Mou signé', selection=[('OUI','OUI'),('NON','NON')], required=False, )
    com_part_mou_signe= fields.Text(string='commentaire partenaire mou signe')
    ongportee=fields.Boolean(string='ONG portée')
    nomongportee=fields.Char('Nom ONG portée')
    partongportee=fields.Float(string='Part ONG portée')
    ongport_mou_signe= fields.Selection(string='Mou signé', selection=[('OUI','OUI'),('NON','NON')], required=False, )
    com_ongport_mou_signe=fields.Text(string='commentaire ong portée mou signe')
    suiviversement = fields.One2many('crm.alima.reporting.suiviversement', 'lead', string='Suivi des versements')
    rapport = fields.One2many('crm.alima.reporting.rapport', 'lead', string='Rapport')
    Infosmission = fields.One2many('crm.alima.reporting.infosmission', 'lead', string='Infos mission')
    mr = fields.One2many('crm.alima.reporting.mr', 'lead', string='MR')
    montant_total_versement= fields.Float(string='Montant total versement', compute='compute_montant_versement')
    depensestotales=fields.Float(string='dépenses totales')
    depenseautorisees=fields.Float(string='dépenses autorisées')
    reliquat=fields.Integer(string='reliquat')
    date_reliquat = fields.Date(string='Date reliquat')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'crm.lead')], string='Attachments')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    url_redirection = fields.Char(String='Url de redirection', compute='compute_generate_url')
    differerence_day = fields.Integer(store=True, default=0)

    @api.multi
    def send_mail_template(self):
        # self.ensure_one()
        #print 'self', self
        #print 'Elimane NDOME envoie par mail'
        all_contrats = self.env['crm.lead'].search([])
        for contrat in all_contrats:
            if contrat.name == 'NE1401':
                #print 'nom: -------------------------------------'
                #print contrat.name
                today = datetime.now()
                if contrat.date_fin:
                    #print 'elimane aujourdhui'
                    #print today
                    #print 'date fin'
                    dt = datetime.strptime(contrat.date_fin, '%Y-%m-%d')
                    #print dt
                    time_to_birthday = (dt - today)
                    #print 'elimane diffrerence'
                    #print time_to_birthday
                    #print time_to_birthday.total_seconds()
                    #print time_to_birthday.total_seconds()/86400
                    contrat.write({
                        'differerence_day': time_to_birthday.total_seconds()/86400
                    }) 

                    # Find the e-mail template
                    template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_mail_alima')
                    # Send out the e-mail template to the user
                    self.env['mail.template'].browse(template.id).sudo().send_mail(contrat.id)
                    #if int(time_to_birthday.days) <= 30:
                    #    print 'elimane notification 30'
                    """
                    current_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    print current_url

                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    if base_url and base_url[-1:] != '/':
                        base_url += '/'
                    db = self._cr.dbname
                    print  "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, contrat.id, "crm.lead")
                    """
                    #print contrat.url_redirection
                    #print '--------------------------fin-------------------------------------'

    @api.depends('name')
    @api.one
    def compute_generate_url(self):
        current_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #print current_url
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        #print  "{}web?db={}#id={}&view_type=form&model={}".format(base_url, db, self.id, "crm.lead")
        self.url_redirection = "{}web?db={}#id={}&view_type=form&action=139&menu_id=97&model={}".format(base_url, db, self.id, "crm.lead")


    @api.depends('planned_revenue','montant_bailleur')
    def compture_pourcentage_montant_bailleur(self):
        for rec in self:
            rec.pourcentage_montant_bailleur=0
            if rec.planned_revenue:
                rec.pourcentage_montant_bailleur= (rec.montant_bailleur/rec.planned_revenue)*100

    @api.depends('planned_revenue','montant_bailleur')
    def compture_montant_cofinancement(self):
        for rec in self:
            rec.montant_cofinancement=0
            if rec.planned_revenue:
                rec.montant_cofinancement= rec.planned_revenue - rec.montant_bailleur


    @api.depends('couts_directs','couts_indirects')
    def compute_pour_couts_indirects(self):
        for rec in self:
            rec.pour_couts_indirects=0
            if rec.couts_directs and rec.couts_indirects:
                rec.pour_couts_indirects= (rec.couts_indirects/rec.couts_directs)*100

    @api.depends('suiviversement')
    def compute_montant_versement(self):
        montant = 0
        for rec in self:
            if rec.suiviversement:
               for res in rec.suiviversement:
                   montant = res.versement + montant
            rec.montant_total_versement=montant

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res= super(CrmLeadReporting, self).create(vals)
        self.env['crm.alima.reporting.mr'].create({'lead': res.id,
                                                   'name': 'Initial',
                                                   'datedebut': fields.Date.today(),
                                                   'datefin': fields.Date.today(),
                                                   'commentaire': 'Initial',
                                                   'montant_budget': res.planned_revenue
                                                   })
        return res
    #liste des fonctions
    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'crm.lead'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    @api.multi
    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        action['search_view_id'] = (self.env.ref('crm_alima_reporting.ir_attachment_view_search_inherit_crm_alima_reporting').id, )
        return action

class MR(models.Model):
    _name="crm.alima.reporting.mr"
    _description="MR des contrats"

    name=fields.Char(string='Nom MR')
    duree=fields.Float(string='Duree en mois')
    datedebut = fields.Date(string='Date debut')
    datefin = fields.Date(string='Date fin')
    commentaire=fields.Text(string='Commentaire sur le MR')
    statut=fields.Selection(VALIDATION, string='Statut')
    budget_additionnel=fields.Selection(OUINON, string='budget additionnel')
    montant_budget=fields.Float(string='Montant budget')
    lead = fields.Many2one('crm.lead', string='Contrat', required=True)
    liendocument=fields.Char(string='lien document')

class Rapport(models.Model):
    _name="crm.alima.reporting.rapport"
    _description="Rapport des contrats"

    name=fields.Selection(NOMRAPPORT,string="Nom du rapport")
    type_rapport=fields.Selection(TYPERAPORT, string="type de rapport")
    etat=fields.Selection(ETAPERAPPORT,string="Etat")
    arendre=fields.Date(string='A rendre le')
    langue= fields.Selection(LANGUE, string='Langue')
    date_debut=fields.Date(string="Date debut")
    date_fin=fields.Date(string="Date fin")
    rendu=fields.Selection(OUINON, string="Rendu")
    date_depot=fields.Date(string="Date depot")
    date_interne=fields.Date(string="Date interne")
    commentaire=fields.Text(string='Commentaire sur le rapport')
    lead = fields.Many2one('crm.lead', string='titre contrat', required=True)
    liendocument=fields.Char(string='lien document')
    #color = fields.Integer('Color Index', default=0)

    code_contrat = fields.Char(string ='code contrat',related='lead.code_contrat', store=True)
    bailleur = fields.Char( string='bailleur', related='lead.partner_id.name', store=True)
    url_redirection = fields.Char(String='Url de redirection', compute='compute_generate_url')
    agent_mails = fields.Text(string='Mail agent', help='Les emails sont séparés par des virgules', compute='compute_user_mail')
    manager_mail = fields.Char(string='Mail manager', compute='compute_user_mail')
    financier_mail = fields.Char(string='Mail financier', compute='compute_user_mail')
    mails_to_send = fields.Text(store=True)
    differerence_day = fields.Float(store=True, default=0)
    # pays = fields.Char(related="lead.pays")

    @api.one
    @api.depends('lead')
    def compute_user_mail(self):
        # print "mail financier",self.lead.pays.financier_mail
        # self.financier_mail = self.lead.pays.financier_mail
        liste_mails = []
        
        for country in self.lead.pays:
            liste_mails.append(country.agent_mails.strip()) if country.agent_mails else None
        
        self.agent_mails = ','.join(liste_mails)
        self.manager_mail = self.lead.team_id.manager_mail.strip() if self.lead.team_id and self.lead.team_id.manager_mail else None
        self.financier_mail = self.lead.pays.financier_mail
        #print self.financier_mail


    @api.multi
    def send_mail_template(self):
        #print 'Yacine NDao envoie par mail'
        all_rapports = self.env['crm.alima.reporting.rapport'].search([])
        begin_date = datetime.strptime('2018-12-24 00:00:00', '%Y-%m-%d %H:%M:%S')
        for rapport in all_rapports:
            if rapport.arendre and rapport.lead.name == 'NE1401':
            #Le cron s'execute pour les dates arendre superieures à 24/12/2018
            # if rapport.arendre and datetime.strptime(rapport.arendre, '%Y-%m-%d') >= begin_date: 
                if rapport.rendu != 'OUI':
                    dt = datetime.strptime(rapport.arendre, '%Y-%m-%d')
                    time_to_birthday = (dt - datetime.strptime(str(date.today()), '%Y-%m-%d'))
                    rapport.write({
                        'differerence_day': round(time_to_birthday.total_seconds()/86400)
                    })
                    #print 'difference day', rapport.differerence_day
                    if rapport.differerence_day in [2.0, 7.0, 15.0, 30.0]:
                        #print 'papa'
                        rapport.mails_to_send = rapport.agent_mails
                        # Find the e-mail template
                        template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_rapport_alima')
                        # Send out the e-mail template to the user
                        self.env['mail.template'].browse(template.id).sudo().send_mail(rapport.id)

                    # 2jours de retard    
                    elif rapport.differerence_day == -2.0:
                        rapport.mails_to_send = ','.join([rapport.agent_mails, rapport.manager_mail]) if \
                                                rapport.manager_mail else rapport.agent_mails
                        # Find the e-mail template
                        template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_rapport_alima')
                        # Send out the e-mail template to the user
                        self.env['mail.template'].browse(template.id).sudo().send_mail(rapport.id)

                    # 7jours de retard    
                    elif rapport.differerence_day <= -7.0:
                        rapport.mails_to_send = ','.join([rapport.agent_mails, rapport.manager_mail]) if \
                                                rapport.manager_mail else rapport.agent_mails
                        # Find the e-mail template
                        template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_rapport_alima')
                        # Send out the e-mail template to the user
                        self.env['mail.template'].browse(template.id).sudo().send_mail(rapport.id)
                    else:
                        continue


    @api.multi
    def send_mail_template_financier(self):
        all_rapports = self.env['crm.alima.reporting.rapport'].search([])
        begin_date = datetime.strptime('2018-12-24 00:00:00', '%Y-%m-%d %H:%M:%S')
        for rapport in all_rapports:
            if rapport.arendre and rapport.lead.name == 'NE1401':
            #Le cron s'execute pour les dates arendre superieures à 24/12/2018
            # if rapport.arendre and datetime.strptime(rapport.arendre, '%Y-%m-%d') >= begin_date: 
                if rapport.rendu != 'OUI':
                    dt = datetime.strptime(rapport.arendre, '%Y-%m-%d')
                    time_to_birthday = (dt - datetime.strptime(str(date.today()), '%Y-%m-%d'))
                    rapport.write({
                        'differerence_day': round(time_to_birthday.total_seconds()/86400)
                    })
                    #print 'difference day', rapport.differerence_day
                    if rapport.differerence_day in [2.0,7.0]:
                        # Find the e-mail template
                        template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_rapport_alima_financier')
                        # Send out the e-mail template to the user
                        self.env['mail.template'].browse(template.id).sudo().send_mail(rapport.id)

                    # 2jours de retard    
                    elif rapport.differerence_day == -2.0:
                        # Find the e-mail template
                        template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_rapport_alima_financier')
                        # Send out the e-mail template to the user
                        self.env['mail.template'].browse(template.id).sudo().send_mail(rapport.id)

                    # 7jours de retard    
                    elif rapport.differerence_day <= -7.0:
                        # Find the e-mail template
                        template = self.env.ref('crm_alima_reporting.email_template_opportunity_reminder_rapport_alima_financier')
                        # Send out the e-mail template to the user
                        self.env['mail.template'].browse(template.id).sudo().send_mail(rapport.id)
                    else:
                        continue

    @api.depends('name')
    @api.one
    def compute_generate_url(self):
        current_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #print current_url
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if base_url and base_url[-1:] != '/':
            base_url += '/'
        db = self._cr.dbname
        self.url_redirection = "{}web?db={}#id={}&view_type=form&action=152&menu_id=97&model={}".format(base_url, db, self.id, "crm.alima.reporting.rapport")



class SuiviVersement(models.Model):
    _name="crm.alima.reporting.suiviversement"
    _description="Suivi versement"

    name=fields.Char(string="Nom demande de versement")
    pourcentage_contribution=fields.Float(string='Pourcentage de contribution')
    type=fields.Selection(TYPEVERSEMENT, string='Type versement')
    date_prevue=fields.Date(string="Date prévue")
    date_demande=fields.Date(string="Date demande")
    date_versement=fields.Date(string="Date de versement")
    versement=fields.Float(string="Versement")
    commentaire=fields.Text(string='Commentaire sur le versement')
    lead = fields.Many2one('crm.lead', string='Contrat', required=True)
    liendocument=fields.Char(string='lien document')

class InfosMission(models.Model):
    _name='crm.alima.reporting.infosmission'
    _description='Infos Mission'

    name = fields.Char(string="Nom du document", required=False, )
    emetteur = fields.Char(string="Emetteur", required=False, )
    date = fields.Date(string="Date", required=False, )
    lien = fields.Char(string="Lien", required=False, )
    commentaire = fields.Text(string="Commentaire", required=False, )
    lead = fields.Many2one('crm.lead', string='Contrat', required=True)