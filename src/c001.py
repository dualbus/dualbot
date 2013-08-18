#!/usr/bin/env python
from twisted.words.protocols.irc import IRCClient
from twisted.internet import reactor, protocol
from functools import wraps
import logging
from hooks import Ignorer, Intimidator, Friends, Terminator

def hookable(client_ro, func):

  @wraps(func)
  def run_hooks_and_call(*args, **kwargs):
    logging.debug('hook: %s(%s, %s)' % (func.__name__, args, kwargs))

    client = client_ro # The closed variable is read-only
    try:
      hooks = client.factory.hooks[func.__name__]
      logging.debug(hooks)

      for hook in hooks:

        # Give the hook access to the IRCClient
        if hasattr(hook, 'client'):
          hook.client = client

        result = hook(*args, **kwargs)

        if result is None:
          return result # Abort execution
        else:
          args, kwargs = result

    except KeyError:
      pass # No registered hook

    return func(*args, **kwargs)

  return run_hooks_and_call



class MyIrc(IRCClient, object):
  hookable = (
    #'action',
    #'away',
    #'back',
    #'badMessage',
    #'bounce',
    'connectionMade',
    #'created',
    #'ctcpMakeQuery',
    #'ctcpMakeReply',
    #'ctcpQuery',
    #'ctcpQuery_ACTION',
    #'ctcpQuery_CLIENTINFO',
    #'ctcpQuery_DCC',
    #'ctcpQuery_ERRMSG',
    #'ctcpQuery_FINGER',
    #'ctcpQuery_PING',
    #'ctcpQuery_SOURCE',
    #'ctcpQuery_TIME',
    #'ctcpQuery_USERINFO',
    #'ctcpQuery_VERSION',
    #'ctcpReply',
    #'ctcpReply_PING',
    #'ctcpUnknownQuery',
    #'ctcpUnknownReply',
    #'dataReceived',
    #'dccAcceptResume',
    #'dccDoAcceptResume',
    #'dccDoChat',
    #'dccDoResume',
    #'dccDoSend',
    #'dccResume',
    #'dccSend',
    #'dcc_ACCEPT',
    #'dcc_CHAT',
    #'dcc_RESUME',
    #'dcc_SEND',
    #'handleCommand',
    #'irc_ERR_NICKNAMEINUSE',
    #'irc_ERR_PASSWDMISMATCH',
    #'irc_JOIN',
    #'irc_KICK',
    #'irc_MODE',
    #'irc_NICK',
    #'irc_NOTICE',
    #'irc_PART',
    #'irc_PING',
    #'irc_PRIVMSG',
    #'irc_QUIT',
    #'irc_RPL_BOUNCE',
    #'irc_RPL_CREATED',
    #'irc_RPL_ENDOFMOTD',
    #'irc_RPL_LUSERCHANNELS',
    #'irc_RPL_LUSERCLIENT',
    #'irc_RPL_LUSERME',
    #'irc_RPL_LUSEROP',
    #'irc_RPL_MOTD',
    #'irc_RPL_MOTDSTART',
    #'irc_RPL_MYINFO',
    #'irc_RPL_NOTOPIC',
    #'irc_RPL_TOPIC',
    #'irc_RPL_WELCOME',
    #'irc_RPL_YOURHOST',
    #'irc_TOPIC',
    #'irc_unknown',
    #'isupport',
    #'join',
    'joined',
    #'kick',
    'kickedFrom',
    #'leave',
    'left',
    #'lineReceived',
    #'luserChannels',
    #'luserClient',
    #'luserMe',
    #'luserOp',
    #'me',
    #'mode',
    'modeChanged',
    #'msg',
    #'myInfo',
    'nickChanged',
    #'notice',
    'noticed',
    'ping',
    #'pong',
    'privmsg',
    #'quirkyMessage',
    #'quit',
    #'receivedMOTD',
    #'register',
    #'say',
    #'sendLine',
    #'setNick',
    'signedOn',
    #'topic',
    'topicUpdated',
    'userJoined',
    'userKicked',
    'userLeft',
    'userQuit',
    'userRenamed',
    #'whois',
    #'yourHost',
    )

  def __getattribute__(self, name):
    original = object.__getattribute__(self, name)
    if name in MyIrc.hookable:
      return hookable(self, original)
    else:
      return original

  def signedOn(self):
    IRCClient.signedOn(self)

    for channel in self.factory.config['irc.channels']:
      logging.debug('joining: %s' % channel)
      self.join(channel)


  def _nick(self):
    return self.factory.config['irc.nick']
  def _set_nick(self, nick):
    self.factory.config['irc.nick'] = nick

  def _user(self):
    return self.factory.config['irc.user']
  def _set_user(self, user):
    self.factory.config['irc.user'] = user

  def _real(self):
    return self.factory.config['irc.realname']
  def _set_real(self, real):
    self.factory.config['irc.realname'] = real

  nickname = property(_nick, _set_nick)
  username = property(_user, _set_user)
  realname = property(_real, _set_real)



class MyIrcFactory(protocol.ClientFactory):
  protocol = MyIrc

  def __init__(self, config, hooks=None):
    self.config = config

    if hooks is None:
      self.hooks = {}
    else:
      self.hooks = hooks

  def hook(self, action):
    logging.debug('hook: %s' % action)
    try:
      return self.hooks[action]
    except KeyError:
      return None

  def add_hook(self, action, hook):
    logging.debug('add_hook: %s %s' % (action, hook))
    try:
      self.hooks[action].append(hook)
    except KeyError:
      self.hooks[action] = [hook]



if __name__ == '__main__':
  config = {
    'irc.nick': 'dualbot',
    'irc.user': 'dualbot',
    'irc.realname': 'Eduardo Bustamante',
    'irc.network': 'irc.freenode.net',
    'irc.port': 6667,
    'irc.channels': ['#dualbus', '#banning-test'],
    }

  logging.basicConfig(level=logging.DEBUG)

  terminator = Terminator('dualbus')
  friends = Friends({'dualbus': 1})
  factory = MyIrcFactory(config)
  #factory.add_hook('privmsg', Ignorer())
  #factory.add_hook('privmsg', friends.privmsgHook())
  factory.add_hook('privmsg', terminator.privmsgHook())
  #factory.add_hook('userJoined', Intimidator('dualbus', ['#dualbus']))

  reactor.connectTCP(config['irc.network'], config['irc.port'], factory)
  reactor.run()
