from core import Hook

class Ignorer(Hook):
  def __call__(self, user, channel, msg):
  
    cool = ('dualbus',)
    username, _ = user.split('!')
  
    if username in cool:
      return ((user, channel, msg), {})
    else:
      return None
