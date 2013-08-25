from collections import defaultdict
from core import Hook

class Killer(object):
  def __init__(self, rules):
    self.table = defaultdict(dict)
    self.rules = rules

  def execute(self, user):
    if user not in self.table:
      return False

    table = self.table[user]

    if 'channels' not in table:
      return False

    if 'VERSION' not in table:
      return False

    for rule in self.rules:
      if rule(self.table[user]):
        return True

    return False 

  def userJoinedHook(self):
    return Killer.userJoined(self)

  def ctcpReplyHook(self):
    return Killer.ctcpReply(self)

  class common(Hook):
    def __init__(self, killer):
      self.killer = killer

  class userJoined(common):
    def __call__(self, user, channel):

      try:
        self.killer.table[user]['channels'].append(channel)
      except KeyError:
        self.killer.table[user]['channels'] = [channel]

      self.client.ctcpMakeQuery(user, [('VERSION', None)])

      return ((user, channel), {})

  class ctcpReply(common):
    def __call__(self, user, channel, messages):

      nick = user.split('!')[0]

      for tag, data in messages:
        if tag in ['VERSION']:
          self.killer.table[nick][tag] = data

      if self.killer.execute(nick):
        for channel in self.killer.table[nick]['channels']:
          #self.client.mode(channel, True, 'b', user=nick)
          self.client.kick(channel, user=nick)
        self.client.msg(nick, 'You have been banned')

      return ((user, channel, messages), {})
