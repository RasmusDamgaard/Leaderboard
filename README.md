# Board Game Leaderboard
### Video Demo:  <https://youtu.be/2AG26AJPFXA>
### Description:
I have created a web application that can keep track of the ranking and scores from my board game nights with my friends.
### Motivation:
I play a variety of boardgames with friends but we dont keep track of scores. This is important as to know which person has the right to brag! Therefore I 
thought it would be fun to build a leaderboard where my freinds and I can add games and points for each round we play, such that we can always look back and see how we 
fared in different games historically.

### Application details:
The web application is written in Python using the Flask framework. Sqlite3 is used for database management. The application uses the CS50 library for accessing databases. The "requirements.txt" specifies which Python libraries are needed to run the application.

The "app.py" is the python script that contains the backend part of the web application. The application lets user register, login or logout, add new games and add scores for each round of a game played.

"database.db" contains the data. I used DB Browser for SQlite to quickly poke inside the database.

"Templates" contains all html pages which are rendered by app.py.

"static/js" and "static/css" contains javascript and css code for the bootstrap multiselect component used for implementing the dropdown select list in the ranking/overview page.

### Development issues worth mentioning
I did spend quite som time figuring out how to dynamically create the number of buttons appearing on the webpage when adding a new score. Boardgames can have different player counts and only wanted users to be able to add scores for the player count for a specific game. The issue was that i needed to figure out how to get the page to send a POST request when a game was selected from the drop down list and another POST request when information had been filled in by the user. Using the command "onchange="document.f.submit()" helped me achieve this.

Another issue I ran into was the need to do bulk insertion into the SQL database. When users added a score i would have liked that the auto incremented row id would be the same for all players for a given game round. But i never found out how to do the bulk insert. Instead i used a for loop. But this made it difficult to transform the data from the scores table and into a nice format for the table showing scores for each game round. 

The last main obstacle I had was implementing a multiselect dropdown list used for filtering which players one wants to look at in the score overview. I ended up installing a custom multiselect component developed by David Stutz (https://davidstutz.github.io/bootstrap-multiselect/). But for it to work with Bootstrap 5 i had to make a custom installation of the javascript and css files. 

### Future improvements:
The site could use more statistics and visualizations of results. In addition before i can publish the site i need some sort of authorization procedure such that I need to approve poeple before they can finalize their user registration. Further, the aestethics of the website could be improved. 