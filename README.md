Author: Christian Land

Date: 2022

Technologies Used: Python, Flask, Bcrypt, MySQL, XlsxWriter, Requests
# Terminal Archiver

This project scrapes several shipping terminal websites, stores the data in a MySQL database, and then allows users to filter and display that data on the webpage.

# Index Page
![Index](./screenshots/index.png?raw-true "Index")
- Able to login with an email that has been granted access to the website.
- Logging in navigates you to the search page
------------
# Search Page
![Search](./screenshots/search2.png?raw=true "Search")
- Able to filter archived data by terminal, steam-ship line, container, and date
- Able to fetch current data from all of the terminal websites with the "Fetch current data" button
- Able to download the results of the last search as an excel sheet
------------
# Settings Page
![Settings](./screenshots/settings.png?raw=true "Settings")
- Clicking the logged-in user's name in the navbar will take you to the settings page
- If the logged-in account has admin privelages they are able to
    - grant access to the website to different emails
    - update the account level of users that have an account level less than their own
    - update the authentication credentials for the different terminal websites
- Able to change password
