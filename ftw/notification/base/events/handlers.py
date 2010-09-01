from DateTime import DateTime
from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.events.events import NotificationEvent
from ftw.notification.base.interfaces import INotifier
from Products.CMFCore.interfaces._content import IContentish
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapter
from zope.component import getMultiAdapter
from Products.CMFPlone.utils import safe_unicode
from zope.event import notify



def NotificationHandler(event):
    """
    """
    obj = event.obj
    comment = event.comment
    try:
        notifier = INotifier(obj)
    except:
        return

    if event.action is None:
        action = _(u"label_send_notification", default=u"Send Notification")
    else:
        action = event.action

    if event.actor is None:
        portal_state = getMultiAdapter((obj, obj.REQUEST),
                                        name=u'plone_portal_state')
        actor = portal_state.member().getId()
    else:
        actor = event.actor

    if event.time is None:
        time = DateTime()
    else:
        time = event.time

    notifier(kwargs=dict(action=action, comment=comment,
                        actor=actor, time=time))

def object_edited(object_, event):
    sp = getToolByName(object_, 'portal_properties').site_properties
    use_view_action = object_.Type() in  sp.getProperty('typesUseViewActionInListings', ())
    
    if len(object_.REQUEST.get('to_list', [])):
        comment = object_.REQUEST.get('comment', '').replace('<', '&lt;').replace('>', '&gt;')
        comment = safe_unicode(comment)
        notify(NotificationEvent(object_, comment))
        object_.REQUEST.RESPONSE.redirect(object_.absolute_url() + (use_view_action and '/view' or '') )
    else:
        IStatusMessage(object_.REQUEST).addStatusMessage(_(u'statusmessage_no_recipients'), type='error')
        object_.REQUEST.RESPONSE.redirect(object_.absolute_url() + '/notification_form')            
