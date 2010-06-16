from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from ftw.notification.base.events.events import NotificationEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from ftw.notification.base import notification_base_factory as _



class NotificationForm(BrowserView):

    template = ViewPageTemplateFile('notification_form.pt')

    def __init__(self, context, request):
        super(BrowserView,self).__init__(context, request)
        self.pre_select = []

        self.pre_select.append(self.context.REQUEST.get('head_of_meeting', None))
        self.pre_select.append(self.context.REQUEST.get('recording_secretary', None))
        for attendee in self.context.REQUEST.get('attendees', []):
            if attendee.get('contact'):
                self.pre_select.append(attendee.get('contact'))
        for user in self.context.REQUEST.get('users', []):
            if len(user):
                self.pre_select.append(user)
    
    def send_notification(self):
        """ """
        sp = getToolByName(self.context, 'portal_properties').site_properties
        use_view_action = self.context.Type() in  sp.getProperty('typesUseViewActionInListings', ())
        
        if len(self.request.get('to_list', [])):
            comment = self.request.get('comment', '').replace('<', '&lt;').replace('>', '&gt;')
            notify(NotificationEvent(self.context, comment))
            self.request.RESPONSE.redirect(self.context.absolute_url() + (use_view_action and '/view' or '') )
        else:
            IStatusMessage(self.request).addStatusMessage(_(u'statusmessage_no_recipients'), type='error')
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/notification_form')            

    def getAssignableUsers(self):
        """Collect users with a given role and return them in a list.
        """
        context = self.context.aq_inner
        role = 'Reader'
        results = {}
        pas_tool = getToolByName(context, 'acl_users')
        utils_tool = getToolByName(context, 'plone_utils')
        
        inherited_and_local_roles = utils_tool.getInheritedLocalRoles(self.context.aq_parent) + pas_tool.getLocalRolesForDisplay(self.context.aq_inner)
            
        for user_id_and_roles in inherited_and_local_roles:
            if user_id_and_roles[2] == 'user':
                if role in user_id_and_roles[1]:
                    user = pas_tool.getUserById(user_id_and_roles[0])
                    if user:
                        results['%s (%s)' % (user.getProperty('fullname', ''), user.getId())] = user.getId()
            if user_id_and_roles[2] == 'group':
                if role in user_id_and_roles[1]:
                    for user in pas_tool.getGroupById(user_id_and_roles[0]).getGroupMembers():
                        results['%s (%s)' % (user.getProperty('fullname', ''), user.getId())] = user.getId()

        keys = results.keys()
        keys.sort()
        return [[results[k],k] for k in keys]
