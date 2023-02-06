# flaskApp_EC2
A small flask app on EC2

How to run:
  1. download the given files
  2. create a folder with name tmp in the same folder where the app.py reside.
  3. Install the required modules.
  4. create the database
      i) Goto inside the folder
      ii) Enter into python shell
      iii) type in command - 'from app import db'
      iv) then type - 'db.create_all()'
  5. Run the flask server - 'flask run' or 'python app.py'
