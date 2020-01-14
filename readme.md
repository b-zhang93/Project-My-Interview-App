CS50 Final Project 2019

Video Demo: https://youtu.be/dkSTLBohHIA 

My-Interview Web Application:

A simple web application that allows users to sign up and create their own personal interview application that simulates a virtual interview with users they share the link to.
After signing up, users can select an avatar and then input the questions and answers for their virtual interview. They can also choose whether these questions will be Behavioral or Technical.
The application then stores these into an SQL database and outputs it all into an interactable application in which interviewers can conduct a virtual interview of the user.
The application is made to simulate a general / basic interview that individuals can put onto their webpages or resumes and allow employers or recruiters to get to know them a little bit better.
We hope that this can make it fun for recruiters to learn more about their candidates as well as give individuals an upper edge on their portfolio and help them stand out.
The application has dynamic speech bubbles that will change based on the question interviewers select. To demo click here: <link>


What was Done:

- Created a SQL database from scratch to store user information and their question / answers in another table that is linked by user id. All questions / answers are assigned a unique question ID.

- Created a full website with python / flask for backend and HTML/ CSS and Java Script / JQUERY for front end. Website requires registration and log in to create their own application.
  New users are assigned a unique user ID in the database an all their settings for the application are saved for future access.

- Once registered, users are able to set-up the application by inputting their question / answers and selecting a personal avatar to show up in the application for interviewers. The webpage
  stores all data the user changed and submitted and allows users to update, delete, and add information as needed.

- Allows the user to demo a preview of the application based on their set up and avatar choice. They can play as the interviewer and see exactly what others will see in the final product.

- Generates a unique shareable link that allows user to share the final application on the internet with anyone. Whoever accesses the shareable link can view the application and conduct a virtual interview
  of the user. The shareable link is unique for the individual and pulls information from the database based on the URL link. The application will change avatar and question / answer / name based on the
  individual’s unique link. Persons with the link do not need to log in to view the application and can interact and conduct a virtual interview

- Added validation and error pages / alerts for the website at both front end and back end (in case front end fails)

- FAQ 
