# Habit trainer app (**BETA**)
(**NOTE: payment and habit credit system not properly implemented yet**)
An app that pays you to maintain your habits! Watch ads as you do your habits and get paid in gift cards.

Built in python with kivy for planned android implementation. App not tested in Android environment, but works perfectly fine on desktop.
Web page components programmed with HTML, Javascript, and PHP. Online database made in mySQL.

## Current features:
* habit tracking and storage on your local device with SQLite files
* a streak system (get more money for your habits the more days in a row you do them)
* opens a url to our website in your browser for account creation and ad serving (ex: https://www.radicool.club/habit-tracker-page?username=example@example.com&duration_seconds=60&streak=1)
---
## todo:
### Fundamental:
  * actual advertisements on website
  * Partnership with a gift card company like Tremendous
  * Need to analyze ad revenue to determine sustainable payout amount for habits  
    
  * better weekly habits implementation
  * package into an android APK with buildozer + android testing
    *	use plyer library for notifications and support for other phone stuff 

### Other
* improve UI
* more settings
* 2FA with an authenticator app
* more flashy particle effects for streaks

## Future features
* more 'gameplay' shenanigans, like a 'hardcore' mode (habits done multiple times a day MUST be all be done, otherwise streak resets entirely for the habit) 
* raffles and competitions
* bonus codes
