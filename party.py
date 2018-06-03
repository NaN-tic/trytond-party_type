#This file is part party_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Equal, Eval, Not, Or, Bool
from trytond.transaction import Transaction

__all__ = ['Party']


STATES_PERSON = {
    "readonly": Or(
        Not(Bool(Eval('active'))),
        Not(Equal(Eval('party_type'), 'person'))),
    "invisible": Not(Equal(Eval('party_type'), 'person')),
}
STATES_PERSON_DEPENDS = ['active', 'party_type']


class Party:
    __metaclass__ = PoolMeta
    __name__ = "party.party"

    party_type = fields.Selection(
        [
            ("organization", "Organization"),
            ("person", "Person"),
        ], "Type", select=True, states={
            'readonly': Not(Bool(Eval('active'))),
        }, depends=['active'])
    first_name = fields.Char(
        "First Name", states=STATES_PERSON, depends=STATES_PERSON_DEPENDS)
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            (None, ""),
        ], "Gender", select=True, sort=False,
        states=STATES_PERSON, depends=STATES_PERSON_DEPENDS)

    @staticmethod
    def default_party_type():
        """Party.default_party_type()
        This method sets the default value for field type, depending
        on the context defined in party_type.xml.
        """
        return Transaction().context.get('party_type', 'organization')

    def get_rec_name(self, name):
        """Party.get_rec_name(self, name)
        This method combines last and first name for views.
        The kind of combination of first and last names may vary from
        country to country. The pattern used here is::

            <last_name>, <first_name>

        Overwrite this method for other conventions of person names.
        """
        return ", ".join(
            x for x in [self.name, self.first_name] if x)

    @classmethod
    def search_rec_name(cls, name, clause):
        """Party.search_rec_name(name, clause)
        This method adds the first name to search clause for searching persons.
        """
        domain = super(Party, cls).search_rec_name(name, clause)
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            domain,
            ('name',) + tuple(clause[1:]),
            ('first_name',) + tuple(clause[1:]),
            ]

    @fields.depends('party_type')
    def on_change_party_type(self):
        '''
        Method to clear party attributes, when changing a party with
        party type 'person' to type 'organization'.
        '''
        party_type = self.party_type if self.party_type else 'organization'
        if party_type == 'organization':
            self.party_type = party_type
            self.first_name = None
            self.gender = None

    def get_full_name(self, name):
        """Party.get_full_name(self, name)
        This method overwrites the standard full name as used in reports
        to call the name of a person party. The kind of combination of
        first and last names may vary from country to country.
        The pattern used here is::

        <first_name> <last_name>

        Overwrite this method for other conventions of person names.
        """
        return " ".join(
            x for x in [self.first_name, self.name] if x)
