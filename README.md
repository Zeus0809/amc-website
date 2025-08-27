## Key takeaway from Docker containerization:

The database URI should be relative to the ROOT of whatever context the app is running in, not relative to WORKDIR.

This was causing a SQLite error:
DATABASE_URL=sqlite:///instance/amc_website.db

This is working:
DATABASE_URL=sqlite:////amc-website/instance/amc_website.db

It works because /amc-website/instance/amc_website.db is the path of the DB file inside the container. That's what db.create_all() wants to access.

