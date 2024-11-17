This is a browser based file sharing device.
Author is only myself.

This project will be built in python with Flask. 
responsibilities
    File management: Handle requests for uploading, downloading, and deleting files in the shared folder.
    
    Authentication: Ensure only authorized users can acces files, especially if hosted on a public network.

    Notifications: Notifyu connected clients of new or modified files.

Shared file directory
    The actual directory on the server where files are stored should be shared.
    Implement monitoring using watchdog to detect changes

Later on there will also be built a database for this project using either some form of SQL.

A Front-End interface
    A simple HTML and JS interface that lets user browse files, upload new files, and download existing ones.

The users need to enter the server's IP address and port in the browser to enter the website.

