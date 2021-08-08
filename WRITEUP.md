### Monthly Cost Analysis
A one month cost analysis of each Azure resource is as listed below:


|Azure Resource|Service Tier|Monthly Cost|
|---|---|---|
|Azure Postgres Database|Basic|\$24.82 (1 core) + \$5.00 (min 50GB storage)|
|Azure Service Bus|Basic|$0.05 (per million operations)|	
|Azure Web Service|Free|\$0 (shared 60 CPU minutes / day)
|Azure Function App|Consumption|\$0 (free grant of 1 million executions per month)|

The total estimated monthly cost is **\$29.87 / month**.

---	

### Architecture Explanation

For the Azure Web App, 

1. Upon clicking the `Send Notification` button, the Flask web app will write the information, i.e. `Notification Subject` and `Notification Message` into the Azure PostgreSQL database's `notification` table, with the status tag `Notification submitted`.

2. After that, it will send a notification message (which contains the primary key id of the submitted notification in the Azure PostgreSQL database `notification` table) to the Azure Service Bus Queue. 

See line 58 to 101 in <a href='web/app/routes.py'>routes.py</a>

<br/>

For the Azure Function App,

1. Upon receiving the Azure Service Bus Queue trigger (with the notification id), the function app will read the `Notification Subject` and `Notification Message` from the Azure PostgreSQL database's `notification` table, corresponding to the incoming id.

2. Next, it will read all attendee information from the Azure PostgreSQL database's `attendee` table, and send the email to each attendee.

See line 10 to 76 in <a href='function/ServiceBusQueueTrigger/__init__.py'>\_\_init\_\_.py</a>

<br/>

The advantage of this architecture is that is separates/decouples the functionality of sending notification emails from the web UI client. By having a standalone Azure Function App service that responds to Azure Service Bus Queue messages, we can support various client types (e.g. mobile app, PC app, etc) as long as they can send queue messages to the Service Bus. Thus, we do not need to implement the same functionality across multiple client types.

---

### Screenshots


1. Migrate Web Applications - 2 Screenshots
    - Screenshot of Azure Resource showing the App Service Plan.

        <img src='images/Screenshot 2021-08-07 22:21:16(1).png'>
    - Screenshot of the deployed Web App running. The screenshot should be fullscreen showing the URL and application running.
        <img src='images/Screenshot 2021-08-07 22:20:03.png'>
        
2. Migrate Database - 2 Screenshots
    - Screenshot of the Azure Resource showing the Azure Database for PostgreSQL server.
        <img src='images/Screenshot 2021-08-07 22:32:16(1).png'>
    - Screenshot of the Web App successfully loading the list of attendees and notifications from the deployed website.
        <img src='images/Screenshot 2021-08-07 22:25:45.png'>
        <img src='images/Screenshot 2021-08-07 22:27:17.png'>
3. Migrate Background Process - 4 Screenshots
    - Screenshot of the Azure Function App running in Azure, showing the function name and the function app plan.
        <img src='images/Screenshot 2021-08-08 01:09:37.png'>
    - Screenshots of the following showing functionality of the deployed site:
        - Submitting a new notification.
            - Screenshot of filled out Send Notification form.
                <img src='images/Screenshot 2021-08-08 00:34:03.png'>
        - Notification processed after executing the Azure function.
            - Screenshot of the Email Notifications List showing the notification status as Notifications submitted.
                <img src='images/Screenshot 2021-08-08 01:17:55.png'>
            - Screenshot of the Email Notifications List showing the notification status as Notified X attendees.
                <img src='images/Screenshot 2021-08-08 01:18:56.png'>
