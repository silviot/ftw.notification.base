from ftw.table.interfaces import ITableGenerator
from Products.Five.browser import BrowserView
from zope import schema
from zope.component import queryUtility
from Products.CMFPlone.utils import safe_unicode
from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.events.handlers import object_edited

def name_helper(item, value):
    title = safe_unicode(item['title'], 'utf-8')
    value = safe_unicode(item['value'], 'utf-8')
    val = u'%s (%s)' % (title, value)
    return val

def groupname_helper(item, value):
    title = safe_unicode(item['title'], 'utf-8')
    val = u'%s' % title
#   bei klick alle user anzeigen? js
#    val = u'<a href="#" class="showUsers" title="groupid">%s</a>' % title
    return val

def checkbox_to_helper(item, value):
    return u"""<input type="checkbox"
                      name="to_list:list"
                      value="%s"/>""" % item['value']

def checkbox_cc_helper(item, value):
    return u"""<input type="checkbox"
                    name="cc_list:list"
                    value="%s"/>""" % item['value']

def checkbox_to_group_helper(item, value):
    return u"""<input type="checkbox"
                      name="to_list_group:list"
                      value="%s"/>""" % item['value']

def checkbox_cc_group_helper(item, value):
    return u"""<input type="checkbox"
                    name="cc_list_group:list"
                    value="%s"/>""" % item['value']


class NotificationForm(BrowserView):

    columns = (
        {'column': 'to',
         'column_title': _(u'label_to', default='TO'),
         'transform': checkbox_to_helper },
        {'column': 'cc',
         'column_title': _(u'label_cc', default='CC'),
         'transform': checkbox_cc_helper },
        {'column': 'name',
         'column_title': _(u'label_name', default='Name'),
         'transform': name_helper}, )

    columns_group = (
        {'column': 'to',
         'column_title': _(u'label_to', default='TO'),
         'transform': checkbox_to_group_helper },
        {'column': 'cc',
         'column_title': _(u'label_cc', default='CC'),
         'transform': checkbox_cc_group_helper },
        {'column': 'name',
         'column_title': _(u'label_name', default='Name'),
         'transform': groupname_helper}, )


    @property
    def users(self):
        context = self.context
        users = []
        vocabulary = queryUtility(schema.interfaces.IVocabularyFactory,
                               name='ftw.notification.base.users',
                               context=context)
        if vocabulary:
            users = vocabulary(context)
            # TODO: ftw.table cant handle PrincipalTerm yet. We need to
            # convert to a dict for now
            users = [dict(title=t.title, value=t.value) for t in users]
        return users

    @property
    def groups(self):
        context = self.context
        groups = []
        vocabulary = queryUtility(schema.interfaces.IVocabularyFactory,
                               name='ftw.notification.base.groups',
                               context=context)
        if vocabulary:
            groups = vocabulary(context)
            groups = [dict(title=g.title, value=g.value) for g in groups]
        return groups

    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.users, self.columns, sortable = True)

    def render_listing_group(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.groups, self.columns_group, sortable = True)

    def send_notification(self):
        """Manual call the event"""
        
        # set sendNotification in REQUEST
        self.request.set('sendNotification', 1)
        object_edited(self.context, None)
