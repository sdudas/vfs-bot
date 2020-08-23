# vfs-bot
## Automate constantly checking for an appointment on VFS Global UKVI

Hi!  This is pretty hacky and not at all robust but this is the script I wrote so that my computer was able to text me when appointments became available on the VFS website.  Before using it, you'll need to setup the following:
- Selenium webdriver: https://www.selenium.dev (used to automate chrome)
- Twilio free trial: https://www.twilio.com/ (api to build sms applications)
- 2Capcha: https://2captcha.com/ (pay 50c per 1000 correctly solved capchas to login every time your session expires)

The script you need to run is vfsbot.py.  The rest should be explained in the comments!!  

The script may be buggy with regards to timeouts and such - let me know if it isn't working and i can try to figure it out!

Good luck!
