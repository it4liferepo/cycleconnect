# -*- coding: utf-8 -*-
from odoo import models, _,fields, api, exceptions
from odoo.exceptions import UserError, ValidationError
from datetime import date
from odoo import tools
from datetime import datetime
import base64
import logging
import threading
from array import *
import string
import random
import unicodedata


from dateutil import relativedelta
#from workalendar.europe import France
#cal = France()

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
SEXE=[
    ('M', 'M'),
    ('F', 'F'),
    ('C mixte', 'C mixte'),
    ('C M', 'C M'),
    ('C F', 'C F'),
    ('X indetermine', 'X indéterminé')
    ]
TYPE_PERSONNE=[
    ('Personne physique','Personne physique'),
    ('Personne morale','Personne morale'),
    ('Piege','Piège'),
    ('Anonyme','Anonyme'),
]
TITLE =[
    ('M.', 'Monsieur'),
    ('Mme', 'Madame'),
    ('Mlle', 'Mademoiselle'),
    ('M. et Mme', 'M et Mme'),
    ('M et M', 'M et M'),
    ('Mme et Mme', 'Mme et Mme'),
    ('Abbe', 'Abbe'),
    ('DECEDE', 'DECEDE'),
    ('ASSO', 'ASSO'),
]
STATUT =[
    ('Actif', 'Actif'),
    ('Doublon', 'Doublon'),
    ('Radie', 'Radie'),
    ('Ne pas prospecter', 'Ne pas prospecter'),
	('Decede', 'Décédé'),
]
CATEGORIE_ACTIF =[
    ('Mono Donateur', 'Mono Donateur'),
    ('Consolide', 'Consolidé'),
    ('Fidelise', 'Fidélisé'),
]
TAG =[
    ('oui', 'Oui'),
    ('non', 'Non'),
    ('peut-etre', 'Peut-être'),
]
STATUT_SOLL =[
    ('oui', 'Oui'),
    ('non', 'Non'),
    ('peut-etre', 'Peut-être'),
    ('en-cours', 'En cours'),
]
FREQ_COM=[
    ('Prospect','Prospect'),
    ('Nouveau','Nouveau'),
    ('Consolide','Consolidé'),
]
FREQ_DON=[
    ('0-6 mois','0-6 mois'),
    ('6-12 mois','6-12 mois'),
    ('12-18 mois','12-18 mois'),
    ('plus 18 mois', '+18 mois'),
]
DON_MOYEN=[
    ('1-50','1-50€'),
    ('50-250','50-250€'),
    ('250-500','250-500€'),
    ('500 et plus','500€ et plus'),
]
TYPE_HIST_COM=[
    ('Telemarketing','Télémarketing'),
    ('Email','Email'),
    ('Papier','Papier'),
    ('SMS','SMS'),
    ('Evenement','Evénement'),
    ('Fax','Fax'),
    ('Rendez-vous','Rendez-vous'),
]
CAT_GRAND_DONATEUR=[
    ('Middle','Middle'),
    ('Global leader','Global leader'),
    ('Investisseur / fondateur','Investisseur / fondateur'),
]
HIST_SORTANT=[
    ('telemarketing', 'Télémarketing'),
    ('email', 'Email'),
    ('papier', 'Papier'),
    ('sms', 'SMS'),
    ('evenement', 'Evénement'),
    ('fax', 'Fax'),
    ('rendez-vous', 'Rendez-vous'),
]
HIST_ENTRANT=[
    ('plainte', 'Plainte'),
    ('administratif', 'Administratif'),
    ('discussion', 'Discussion'),
    ('demande informations', 'Demande d\'informations'),
]
TYPE_ORGANISATION=[
    ('Entreprise', 'Entreprise'),
    ('Fondation', 'Fondation'),
    ('Asso', 'Asso'),
    ('Fonds dotation',  'Fonds dotation'),
    ('Ecoles', 'Ecoles'),
    ('Autres','Autres'),
]
RETOUR_COURIER=[
    ('0','0'),
    ('1','1'),
    ('2','2'),
    ('NPAI ','NPAI (3 retours)'),
]
TRAITEMENT_ADRESSE=[
    ('RNVP','RNVP'),
    ('Charade-Estocade','Charade-Estocade'),
    ('Autre','Autre'),
]
TYPE_ARRET=[
    ('Non sollicitable','Non sollicitable'),
    ('Sollicitable Don', 'Sollicitable Don'),
    ('Sollicitable PA','Sollicitable PA'),
]
RECENCE=[
    ('Actif','Actif'),
    ('Inactifs recents','Inactifs récents'),
    ('Inactifs','Inactifs'),
    ('Grands inactifs','Grands inactifs'),
]
MONTANT=[
    ('Donor','Donor'),
    ('Middle donor','Middle donor'),
    ('Global Leader','Global Leader'),
    ('Investisseur Fondateur','Investisseur / Fondateur'),
]
STATUT_LEGS=[
    ('interesse', 'interesse'),
    ('testataire', 'testataire'),
    ('dossier legs en cour', 'dossier legs en cour'),
]
OUINONVIDE=[
    ('Vide','Vide'),
    ('Oui','Oui'),
    ('Non','Non'),
]
RF=[
    ('regulier','Régulier'),
    ('annuel','Annuel'),
    ('non','Non'),
    ('recurrent','Récurrent '),
]
COURRIER=[
    ('0','0'),
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4', '4'),
    ('Tous','Tous'),
]
SENS_SOLL=[
    ('entrant','Entrant'),
    ('sortant','Sortant'),
]
CANAL=[
    ('courrier','Courrier'),
    ('telephone','téléphone'),
    ('email','email'),
    ('fax','fax'),
    ('SMS','SMS'),
    ('face a face','face à face'),
    ('evenement physique','événement (physique)'),
    ('rendez-vous','Rendez-vous'),
    ('reseaux sociaux','réseaux sociaux'),
    ('messagerie instantannee','messagerie instantannée'),
]
TYPE_CONTACT=[
    ('administratif','Administratif'),
    ('demande information','Demande information'),
    ('plainte','Plainte'),
    ('Discussion','Discussion'),
]
QUALIF=[
    ('positif','Positif'),
    ('negatif','Négatif')
]
STATUT_TRAIT=[
    ('Oui','Oui'),
    ('non','non'),
    ('en_cours','en cours'),
]
ADHERANT=[
    ('oui','Oui'),
    ('non','Non'),
    ('en_cours','en cours'),
]
TELEMARK=[
    ('non appele','Non appelé'),
    ('non-joint','Non-Joint'),
    ('joint non utile','Joint Non-Utile'),
    ('joint utile','Joint Utile'),
]
CANAL2=[
    ('courrier', 'courrier'),
    ('email', 'email'),
]
MOTIF_FIN_ENGAGEMENT = [
    ('decision_solthis', 'Décision solthis'),
    ('upgrade', 'Upgrade'),
    ('downgrade', 'downgrade'),
    ('incidents_paiement', 'Incidents de paiement'),
    ('autres', 'Autres'),
]

PERIODICITE = [
    ('un_mois', '1 mois'),
    ('deux_mois', '2 mois'),
    ('trois_mois', '3 mois'),
    ('quatre_mois', '4 mois'),
    ('six_mois', '6 mois'),
    ('douze_mois', '12 mois'),
]

PERIODICITE_MOIS_EN_ENTIER = {
    'un_mois': 1,
    'deux_mois': 2,
    'trois_mois': 3,
    'quatre_mois': 4,
    'six_mois': 6,
    'douze_mois': 12,
}

STATUT_ENGAGEMENT = [
    ('actif', 'Actif'),
    ('suspendu_temporairement', 'Suspendu Temporairement'),
    ('inactif', 'Inactif'),
]

MOTIF_MODIFICATION = [
    ('erreur', 'Erreur'),
    ('modification', 'Modification'),
    
]

MOIS = {
    1: 'Janvier',
    2: 'Fevrier',
    3: 'Mars',
    4: 'Avril',
    5: 'Mai',
    6: 'Juin',
    7: 'Juillet',
    8: 'Aout',
    9: 'Septembre',
    10: 'Octobre',
    11: 'Novembre',
    12: 'Decembre',
}
CHER={
    'Monsieur':'Cher',
    'Madame':'Chère',
    'Mademoiselle':'Chère',
    'M et Mme':'Chère',
    'M et M':'Cher',
    'Abbe':'Cher',
}

STATES = [
    ('draft', 'Brouillon'),
    ('confirmer', 'Importé'),
    ('annuler', 'Annulé'),
]

SEPARATOR = [
    ('virgule', 'virgule'),
    ('point_virgule', 'point virgule'),
    ('pipe', 'pipe'),
]

CORRESPONDANCE = {
    'virgule':',',
    'point_virgule': ';',
    'pipe': '|',
}


class IMPORTDONATEURCREDITCOOP(models.Model):
    _name = 'crm.alima.import.donateur.credit.coop'
    _description = 'IMPORT DONATEUR CREDIT COOP'

    @api.onchange('data', 'separator')
    def import_donateur_template(self):
        donateurs = []
        if self.data and self.separator:
            #try:
            data = base64.decodestring(self.data.encode())
            separator = CORRESPONDANCE[self.separator]
            liste_data = [cell.split(separator) for cell in data.decode().replace('\r', '').replace('"','').split("\n")]
            liste_data_remove_space = [[cell.strip() for cell in line] for line in liste_data]
            dicos = self.fusion(liste_data_remove_space)
            #except:
                #raise UserError(_("Erreur d'import, vérifier le séparateur et le fichier chargé"))
            for line in dicos:
                line['partenaire'] = line['partenaire'].replace('False','').replace('false','') if 'partenaire' in line else None
                line['telemarketing'] = line['telemarketing'].replace('False','').replace('false','') if 'telemarketing' in line else None
                line['courrier'] = line['courrier'].replace('False','').replace('false','') if 'courrier' in line else None
                line['sms'] = line['sms'].replace('False','').replace('false','') if 'sms' in line else None
                line['evenement'] = line['evenement'].replace('Non','').replace('non','').replace('False','').replace('false','') if 'evenement' in line else None
                line['option_CNIL'] = line['option_CNIL'].replace('False','').replace('false','') if 'option_CNIL' in line else None
                line['echange_mail'] = line['echange_mail'].replace('False','').replace('false','') if 'echange_mail' in line else None
                line['email3'] = line['email3'].replace('False','').replace('false','') if 'email3' in line else None
                line['id_bulletin'] = line['id_bulletin'].replace('False','').replace('false','') if 'id_bulletin' in line else None
                donateurs.append((0, 0, line))
            self.donateur_credit_coop_line = donateurs
        else:
            self.donateur_credit_coop_line = False



    name = fields.Char(string="Titre", required=True)
    description = fields.Text()
    datetime = fields.Datetime(readonly=True, string='Date import')
    separator = fields.Selection(SEPARATOR, default='point_virgule', required=True, String='Séparateur')
    nombre_de_donateurs_importes = fields.Integer(readonly=True)
    user_import = fields.Many2one('res.users', string="User", readonly=True)
    state = fields.Selection(STATES, default='draft', readonly=True)

    filename = fields.Char('File Name')
    data = fields.Binary('Import PO')

    donateur_credit_coop_line = fields.One2many('crm.alima.donateur.template', 'donateur_credit_coop_id', string='Donateur', required=True)

    @api.model
    def default_get(self, fields):    
        res = super(IMPORTDONATEURCREDITCOOP, self).default_get(fields)        
        if 'user_import' in fields:        
            res.update({
                'user_import' : self.env.user.id,

            })    
        return res

    @api.multi
    def clear_line(self):
        self.donateur_credit_coop_line = False
        self.data = False

    def fusion(self, liste):
        dicos = []
        for i in range(1,len(liste)):
            dicos.append(dict(zip(liste[0], liste[i])))
        for i in range(len(dicos)):
            for key in dicos[i]:
                if 'date' in key and '/' in dicos[i][key]:
                    date = dicos[i][key].split(' ')[0].split('/')
                    date[0], date[2] = date[2], date[0]
                    dicos[i][key] = '-'.join(date)
        return dicos

    @api.multi
    def action_confirmer(self):
        
        if not self.donateur_credit_coop_line:
            raise UserError(_("(re)charger le fichier d'import"))
        
        else:
            donateur = {}
            nombre_de_donateurs_importes = 0
            self.datetime = datetime.today()
            for line in self.donateur_credit_coop_line:
                if line.lastname:
                    donateur = {
                        'title': line.title,
                        'lastname': line.lastname,
                        'firstname': line.firstname,
                        'dateNaissance': line.dateNaissance,
                        'sexe': line.sexe,
                        'type_de_personne': line.type_de_personne,
                        'partenaire': line.partenaire,
                        'raison_sociale': line.raison_sociale,
                        'type_organisation': line.type_organisation,
                        'function': line.function,
                        'sec_activite': line.sec_activite,
                        'complementnom': line.complementnom,
                        'complementadresse': line.complementadresse,
                        'codebis': line.codebis,
                        'hammeau': line.hammeau,
                        'codepostale': line.codepostale,
                        'ville': line.ville,
                        'country_id': line.country_id,
                        'email': line.email,
                        'email2': line.email2,
                        'personal_fone': line.personal_fone,
                        'personal_fone2': line.personal_fone2,
                        'statut': line.statut,
                        'rf': line.rf,
                        'canal_envoi': line.canal_envoi,
                        'telemarketing': line.telemarketing,
                        'email3': line.email3,
                        'courrier': line.courrier,
                        'sms': line.sms,
                        'evenement': line.evenement,
                        'option_CNIL': line.option_CNIL,
                        'echange_mail': line.echange_mail,
                        'comm_preference_contrat': line.comm_preference_contrat,
                        'id_bulletin': line.id_bulletin,
                        'datetime_import': self.datetime,
                    }
                    print('donateur', donateur)
                    donateur = self.env['crm.alima.donateur'].create(donateur)
                    nombre_de_donateurs_importes += 1
            
            self.nombre_de_donateurs_importes = nombre_de_donateurs_importes
            self.state = 'confirmer'
    
    @api.multi
    def action_annuler(self):
        self.state = 'annuler'

    @api.multi
    def action_reset_to_draft(self):
        self.state = 'draft'


    @api.multi
    def action_roll_back(self):
        if self.datetime:
            self.env['crm.alima.donateur'].search([('datetime_import', '=',self.datetime)]).unlink()
        else:
            raise UserError(_("Roll back échoué"))
        self.state = 'draft'

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Peut pas supprimer un import en état %s.')% self.state)
        return super(IMPORTDONATEURCREDITCOOP, self).unlink()

    def compute_name(self, donateur):
        #Regle bug encodage en decodage: caractères spéciaux
        donateur['email'] = donateur['email'].decode('utf-8')
        donateur['firstname'] = donateur['firstname'].decode('utf-8')
        donateur['codepostale'] = donateur['codepostale'].decode('utf-8')
        donateur['lastname'] = donateur['lastname'].decode('utf-8')

        if ('email' in donateur) and (donateur['email'] in ['helene@collecte.alima.ngo','helene@alima-ngo.org']):
                donateur['email'] = ''
        if ('email' in donateur) and donateur['email']:
            name = donateur['email'].replace(' ', '')
        elif ('firstname' in donateur) and ('codepostale' in donateur) and donateur['firstname'] and donateur['codepostale']:
            name = donateur['lastname'].replace(' ','').upper() + donateur['firstname'].title() + str(donateur['codepostale']).replace('.0', '').replace(' ','')
            name = name.replace('-','')
        elif ('codepostale' in donateur) and donateur['codepostale']:
            name = donateur['lastname'].replace(' ','').upper() + str(donateur['codepostale']).replace('.0', '').replace(' ','')
            name = name.replace('-','')
        elif ('firstname' in donateur) and donateur['firstname']:
            name = donateur['lastname'].replace(' ','').upper() + donateur['firstname'].title()
            name = name.replace('-','')
        else:
            name = donateur['lastname'].replace(' ','').upper()
            name = name.replace('-','')

        name = name.replace(' ','')

        #Regle bug decodage en encodage: caractères spéciaux
        donateur['email'] = donateur['email'].encode('utf-8')
        donateur['firstname'] = donateur['firstname'].encode('utf-8')
        donateur['codepostale'] = donateur['codepostale'].encode('utf-8')
        donateur['lastname'] = donateur['lastname'].encode('utf-8')

        return name

    @api.multi
    def fix_bug_date_naissance(self):
        all_donateur_import = self.env['crm.alima.import.donateur.credit.coop'].search([])
        for liste_donateur in all_donateur_import:
            if 'street' in liste_donateur.name:
                data = base64.decodestring(liste_donateur.data)
                separator = CORRESPONDANCE[liste_donateur.separator]
                liste_data = [cell.split(separator) for cell in data.replace('\r', '').replace('"','').split("\n")]
                liste_data_remove_space = [[cell.strip() for cell in line] for line in liste_data]
                dicos = liste_donateur.fusion(liste_data_remove_space)

                for dic in dicos:
                    if 'email' in dic and dic['email']:
                        #dic['email'] = ''
                        name = self.compute_name(dic)
                        if name and dic['dateNaissance']:
                            donateur = self.env['crm.alima.donateur'].search([('name', '=',name)], limit=1)
                            if not donateur:
                                email = name
                                dic['email'] = ''
                                name = self.compute_name(dic)
                                donateur = self.env['crm.alima.donateur'].search([('name', '=',name)], limit=1)

                                donateur.write({
                                    'dateNaissance': dic['dateNaissance'],
                                    'email': email,
                                })
                            else:
                                donateur.write({
                                    'dateNaissance': dic['dateNaissance']
                                })

class DonateurTemplate(models.Model):
    """
    Class Donateur.
    """
    _name = 'crm.alima.donateur.template'
    _description = 'Donateur Template'
    
    #liste des champs de la classe
    title = fields.Selection(TITLE, string='Civilité', store=True)
    lastname = fields.Char(String="Nom", store=True)
    firstname =fields.Char(String="Prenom", store=True)
    dateNaissance=fields.Date(string='Date de naissance', store=True)
    sexe=fields.Selection(SEXE, string="Sexe", store=True)
    type_de_personne=fields.Selection(TYPE_PERSONNE, string="Type de personne", store=True)
    partenaire=fields.Boolean(string="Partenaire", default=False, store=True)
    raison_sociale=fields.Char(string="Raison sociale", store=True)
    type_organisation=fields.Char(string="type d\'organisation", store=True)
    function= fields.Char(string='fonction', store=True)
    sec_activite=fields.Char(string='secteur d\'activité', store=True)
    complementnom=fields.Char(string='Adresse 1 - Libellé de la voie', store=True)
    complementadresse=fields.Char(string='Adresse 1 - Complément adresse', store=True)
    codebis=fields.Char(string='Adresse 1 - Code bis', store=True)
    hammeau=fields.Char(string='Adresse 1 - Hammeau Lieu-dit', store=True)
    codepostale=fields.Char(string='Adresse 1 - Code postal', index=True, store=True)
    ville=fields.Char(string='Adresse 1 - Ville', store=True)
    country_id = fields.Char(string='Adresse 1 - Pays', store=True)
    email = fields.Char(string='Email 1', index=True, store=True)
    email2 = fields.Char(string='Email 2', store=True)
    personal_fone=fields.Char(string='Téléphone personnel 1', store=True)
    personal_fone2=fields.Char(string='Téléphone personnel 2', store=True)
    statut=fields.Selection(STATUT, index=True, string='Statut', store=True)
    rf=fields.Selection(RF, string='frequence envoie RF', store=True)
    canal_envoi=fields.Selection(CANAL2, string="canal", store=True)
    telemarketing = fields.Boolean(string='Télémarketing', default=False, store=True)
    email3 =fields.Boolean(string='Email', default=False, store=True)
    courrier=fields.Selection(COURRIER, string='Courrier (préférence de réception par an)', store=True)
    sms =fields.Boolean(string='SMS', default=False, store=True)
    evenement =fields.Boolean(string='Evénement', default=False, store=True)
    option_CNIL =fields.Boolean(string='CNIL', default=False, store=True)
    echange_mail=fields.Boolean(string='Echange adresse email', default=False, store=True)
    comm_preference_contrat=fields.Text(string='Commentaires préférences de contact', store=True)
    contacts = fields.One2many('crm.alima.contacts', 'donateur', string='Contacts', store=True)
    id_bulletin = fields.Char(store=True)

    donateur_credit_coop_id = fields.Many2one('crm.alima.import.donateur.credit.coop', string='CREDIT COOP', store=True)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        print('vals', vals)
        return super(DonateurTemplate, self).create(vals)