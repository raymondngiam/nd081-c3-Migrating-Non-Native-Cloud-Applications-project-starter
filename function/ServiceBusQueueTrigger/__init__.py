import logging
import os
from datetime import datetime
import azure.functions as func
import psycopg2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import To

def main(msg: func.ServiceBusMessage):
    notification_id = msg.get_body().decode('utf-8')
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_URL'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PW'])

    try:
        # TODO: Get notification message and subject from database using the notification_id
        message=None
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM public.notification where id = '{notification_id}'")
            message = cur.fetchone()

        if (len(message)>0):
            logging.info(f"Found notification: {notification_id}")
            subject=message[5]
            body=message[2]
            submitted_date = message[3]
            logging.info(f"subject: {subject}")
            logging.info(f"message: {body}")

            # TODO: Get attendees email and name
            attendees=None
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM public.attendee ORDER BY id ASC")
                attendees = cur.fetchall()

            if (len(attendees)>0):
                attendee_count = len(attendees)
                logging.info(f"Found {attendee_count} attendees:")
                # TODO: Loop through each attendee and send an email with a personalized subject
                for attendee in attendees:
                    
                    firstname=attendee[1]
                    email=attendee[5]
                    email_body = body
                    email_subject = '{}: {}'.format(firstname, subject)

                    # send email
                    send_email(email,email_subject,email_body)

                # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
                status=f"Notified {attendee_count} attendees"
                completed_date = datetime.utcnow()
                logging.info(f"Status: {status}")
                logging.info(f"Completion time: {completed_date}")
                with conn.cursor() as cur:
                    tablename = 'public.notification'                    
                    columns="(status,message,submitted_date,completed_date,subject)"
                    values=f"('{status}','{body}','{submitted_date}','{completed_date}','{subject}')"
                    cur.execute(f"INSERT INTO {tablename} {columns} VALUES {values}")
                    conn.commit()
            else:
                logging.error("Attendee list is empty.")
        else:
            logging.error(f"Cannot find notification template with id: {notification_id}")

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.close()

def send_email(email, subject, body):
    message = Mail(
        from_email=os.environ['ADMIN_EMAIL_ADDRESS'],
        to_emails=To(email),
        subject=subject,
        plain_text_content=body)

    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    sg.send(message)