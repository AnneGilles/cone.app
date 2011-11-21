import logging
from cone.tile import (
    tile,
    registerTile,
    Tile,
)
from cone.app import security
from cone.app.browser.ajax import ajax_message
from cone.app.browser.layout import ProtectedContentTile
from cone.app.browser.table import (
    Table,
    RowData,
    Item,
    Action,
)
from yafowil.base import factory


logger = logging.getLogger('cone.app')


registerTile('sharing',
             'cone.app:browser/templates/sharing.pt',
             class_=ProtectedContentTile,
             permission='login')


@tile('local_acl', 'cone.app:browser/templates/table.pt',
      permission='manage_permissions')
class SharingTable(Table):
    
    table_id = 'localacltable'
    table_tile_name = 'local_acl'
    default_sort = 'principal'
    default_order = 'asc'
    slicesize = 15
    query_whitelist = ['term']
    
    @property
    def col_defs(self):
        col_defs = [
            {
                'id': 'actions',
                'title': 'Actions',
                'sort_key': None,
                'sort_title': None,
                'content': 'actions',
                'link': False,
            },
            {
                'id': 'principal',
                'title': 'Principal',
                'sort_key': 'principal',
                'sort_title': 'Sort by principal',
                'content': 'string',
                'link': True,
            },
        ]
        for role in security.DEFAULT_ROLES:
            col_defs.append({
                'id': role[0],
                'title': role[1],
                'sort_key': None,
                'sort_title': None,
                'content': 'structure',
                'link': False,
            })
        return col_defs
    
    @property
    def item_count(self):
        term = self.request.params.get('term')
        if term:
            principals = security.search_for_principals('*%s*' % term)
            return len(principals)
        return len(self.model.principal_roles.keys())
    
    def sorted_rows(self, start, end, sort, order):
        rows = list()
        chb = '<input type="checkbox" />'
        term = self.request.params.get('term')
        principal_roles = self.model.principal_roles
        if term:
            principal_ids = security.search_for_principals('*%s*' % term)
        else:
            principal_ids = principal_roles.keys()
        ids = principal_ids
        if order == 'desc':
            ids.reverse()
        for principal_id in ids[start:end]:
            principal = security.principal_by_id(principal_id)
            if not principal:
                logger.warning('principal %s not found' % principal_id)
                continue
            else:
                title = principal.attrs.get('fullname', principal_id)
            row_data = RowData()
            row_data['actions'] = Item(actions=[])
            row_data['principal'] = Item(title)
            ugm_roles = principal.roles
            local_roles = principal_roles.get(principal_id, list())
            for role in security.DEFAULT_ROLES:
                inherited = role[0] in ugm_roles
                local = role[0] in local_roles
                row_data[role[0]] = Item(
                    self._role_column(principal_id, role[0], local, inherited))
            rows.append(row_data)
        return rows
    
    def _role_column(self, id, role, local, inherited):
        props = {
            'class': 'add_remove_role_for_principal',
            'disabled': inherited,
            'format': 'string',
        }
        props['checked'] = local or inherited
        cb = factory('checkbox', name=id, value=role, props=props)
        ret = '<span ajax:target="%s">' % self.nodeurl
        ret = '%s%s</span>' % (ret, cb())
        return ret


@tile('add_principal_role', permission='manage_permissions')
class AddPrincipalRole(Tile):
    
    def render(self):
        model = self.model
        request = self.request
        try:
            principal_id = request.params['id']
            role = request.params['role']
            roles = model.principal_roles
            if not principal_id in roles:
                model.principal_roles[principal_id] = [role]
                return
            existing = set(model.principal_roles[principal_id])
            existing.add(role)
            model.principal_roles[principal_id] = list(existing)
        except Exception, e:
            print e
            message = "Can not add role '%s' for principal '%s'" % (
                role, principal_id)
            ajax_message(self.request, message, 'error')
        return u''


@tile('remove_principal_role', permission='manage_permissions')
class RemovePrincipalRole(Tile):
    
    def render(self):
        model = self.model
        request = self.request
        try:
            principal_id = request.params['id']
            role = request.params['role']
            roles = model.principal_roles
            if not principal_id in roles:
                raise
            existing = model.principal_roles[principal_id]
            existing.remove(role)
            if not existing:
                del model.principal_roles[principal_id]
            else:
                model.principal_roles[principal_id] = existing
        except Exception, e:
            print e
            message = "Can not remove role '%s' for principal '%s'" % \
                (role, principal_id)
            ajax_message(self.request, message, 'error')
        return u''