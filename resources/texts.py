# -------------------- App Text (from BE.txt) --------------------

MAIN_TEXT = """INTRO EULA  - *** (unblock via properties & must be runs as admin!!!)***

This project was later expanded to include creating a Windows "installation program" for the modified client-side file. 
This would make it easier for less technical players to successfully download and install the modification. 
Unfortunately, Windows will typically warn about launching such programs.
because they both:
Have not been digitally "signed" (beyond my financial horizon at this time),
and Have not had 10,000+ Windows users already tell Windows to run this program anyway giving it was Microsoft calls euphemistically a "positive reputation".
The App is a Python to exe conversion and the Python script extracts files it contains; 
the patcher does not have a PE signature, the embedded Python script is not signed with Authenticode and the files encoded within as a base64 string are unmodified, PE signed files.
Uses BattlEye files from "Unturned" third party steam game as a workaround.
"""

PATCHER_TEXT = """
Working BattlEye on Windows 11 (24h2) Insurgency & Day of Infamy standalone games supported only!
Fix client wise BattlEye related crashes/freezes upon launch!

Using this method you can join all servers again as usual!
TIPS: (tag filters include "battleye" via legacy server)

AVOID BLUE SCREEN OF DEATH..%
"""

BLOCKER_TEXT = """
Automatically blocking the servers in the Windows Firewall (How to block fake servers like Fastpath)

How does the spam work and why should you block this?

If you are playing a source engine game infected by these fake servers you will see a number of different servers spam your list that will make you end up on a different server than you thought you would join.
At the moment of writing the Fastpath community is the primary abuser with this method.

When you joined one of these servers you can still join other servers,
but because of the large amount of servers they spam and the fact they can use players joining the servers to fake having a high player amount for a long time it is easy to get trapped back in.

One of the most important reasons to block these servers outright is that by joining them they can use your steam information to fuel their spamming method. 
They capture your steam details including the unique authentication you used to join the server,
and instead of removing this like other servers do when you leave they will instead put your information and nickname on all the other fake servers for as long as your information is valid.
Causing these servers to appear very high up the server list making it hard to avoid them for others because they can spam as many as they want.

On top of this they will fake any information they can, different map names, server names, server names of popular servers you like, player numbers and even ping (Although they fake the ping in game not on the server list). 
And during the times less HL2DM players are online their effect is amplified since it will be harder for steam's server to detect which server has legitimate players online.

Because they constantly change their details and the ports the servers run on blocking them using the in game blocking buttons is almost impossible. This method you can use to block the spam properly.
"""


DISABLER_TEXT = """ 
Using Disabler optional method you can join all servers which are with battleye turned OFF server wise.
TIPS: (tags filters do NOT include "battleye" via legacy server)

Consist of exe files renaming to avoid the usage of BE even if this one has been installed previously!
Only if you plan to get rid off BattlEye service trigger and play on BattlEye DISABLED servers!
"""