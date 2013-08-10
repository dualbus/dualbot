from core import Hook

class Friends(object):
  def __init__(self, friends=None):
    if friends is None:
      self.friends = {}
    else:
      self.friends = friends

  def introduce(self, friend, stranger):
    if friend in self.friends:
      try:
        self.friends[stranger] += 1
      except:
        self.friends[stranger] = 1

  def privmsgHook(self):
    return Friends.privmsg(self)

  class privmsg(Hook):
    def __init__(self, friends):
      self.friends = friends

    def __call__(self, user, channel, msg):
      try:
        command, stranger = msg.split(' ', 1) # split 1 time
        if command == '!introduce':
          self.friends.introduce(user.split('!')[0], stranger)
          self.client.msg(channel, 'ok')

      except ValueError:
        pass # Bad command, ignore it

      return ((user, channel, msg), {})



