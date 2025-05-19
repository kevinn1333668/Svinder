from aiogram import Dispatcher
from . import start, profile, matching, invite

def register_handlers(dp: Dispatcher):
    start.register_handlers(dp)
    profile.register_handlers(dp)
    matching.register_handlers(dp)
    invite.register_handlers(dp) 