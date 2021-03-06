from DateTime import DateTime
from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.events.events import NotificationEvent
from ftw.notification.base.interfaces import INotifier
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from Products.CMFPlone.utils import safe_unicode
from zope.event import notify


def NotificationHandler(event):
    """The Notification Handler receives a Notification event
       and calls the Notifier with the required attributes.
    """
    obj = event.obj
    comment = event.comment
    try:
        notifier = INotifier(obj)
    except TypeError:
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
    # Do nothing if send notification checkbox wasn't checked.
    if not object_.REQUEST.get('sendNotification', False):
        return
    sp = getToolByName(object_, 'portal_properties').site_properties
    use_view_action = object_.Type() in sp.getProperty(
        'typesUseViewActionInListings', ())

    # XXXXXXXXX handle groups

    add_group_members(object_, 'to_list')
    add_group_members(object_, 'cc_list')

    if len(object_.REQUEST.get('to_list', [])):
        comment = object_.REQUEST.get('comment', '').replace('<',
            '&lt;').replace('>', '&gt;')
        comment = safe_unicode(comment)
        notify(NotificationEvent(object_, comment))
        object_.REQUEST.RESPONSE.redirect(
            object_.absolute_url() + (use_view_action and '/view' or ''))
    else:
        IStatusMessage(object_.REQUEST).addStatusMessage(
            _(u'statusmessage_no_recipients',
              default=u"You have to select at least one recipient"),
            type='error')
        object_.REQUEST.RESPONSE.redirect(
            object_.absolute_url() + '/notification_form')


def add_group_members(context, name):
    """ this function adds group members to request if there aren't already
        there.
        name = 'to_list' or 'cc_list'
    """
    to_list = context.REQUEST.get(name, [])
    groups = context.REQUEST.get('%s_group' % name, '')
    if len(groups):
        for gid in groups:
            group_tool = getToolByName(context, 'portal_groups')
            group = group_tool.getGroupById(gid)
            members = group.getAllGroupMemberIds()
            for mid in members:
                if mid not in to_list:
                    to_list.append(mid)
        context.REQUEST.set(name, to_list)
