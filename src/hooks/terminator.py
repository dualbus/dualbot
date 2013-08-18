from core import Hook

class Terminator(Hook):
  def __init__(self, who, where=None):
    self.who = who
    if where is None:
      self.where = []
    else:
      self.where = where

  def __call__(self, user, channel):
    if self.who == user:
      if channel in self.where or len(self.where) <= 0:
        self.client.msg(user, "Yo dawg!")
    return ((user, channel), {})

  def privmsgHook(self):
    return Terminator.privmsg(self)

  class privmsg(Hook):
    def __init__(self, friends):
      self.friends = friends

    def __call__(self, user, channel, msg):
      import re
      if channel == "#banning-test" and re.search(r'chimpout\.com', msg):
        self.client.msg('#banning-test', 'Yo!')
      return ((user, channel, msg), {})
