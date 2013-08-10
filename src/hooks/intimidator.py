from core import Hook

class Intimidator(Hook):
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
