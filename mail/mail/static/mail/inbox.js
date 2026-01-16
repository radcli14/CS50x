document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Respond to click of the submit button on the compose form
  document.querySelector('#compose-form').onsubmit = send_email;

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch emails for the mailbox listed as the argument
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);

      // List the emails that were returned for this mailbox in the emails-view
      emails.forEach(email => {
        // Create a div to hold each email summary
        const email_div = document.createElement('div');
        email_div.className = 'email-summary';
        email_div.classList.add(email.read ? 'email-read' : 'email-unread');

        // Build the title field, dependent on mailbox type
        let title_field = '';
        if (mailbox === 'sent') {
          title_field = 'TO: ' + email.recipients.join(', ');
        } else {
          title_field = 'FROM: ' + email.sender;
        }
          
        // Add email details to the div
        email_div.innerHTML = `
          <h6>${title_field}</h6>
          <p><em>${email.subject}</em> on <span class="text-muted">${email.timestamp}</span></p>
        `;

        // Add an event listener to read the email when clicked
        email_div.addEventListener('click', () => read_email(email.id));

        // Append the email div to the emails-view
        document.querySelector('#emails-view').appendChild(email_div);
      })
  });
}


function read_email(email_id) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

    // Show a temporary header
  document.querySelector('#emails-view').innerHTML = `<h3>Loading Email...</h3>`;

  // Fetch the email by ID
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);

      // Show the email content
      document.querySelector('#emails-view').innerHTML = `
        <h3>From: ${email.sender} <span class="text-muted">at ${email.timestamp}</span></h3>
        <h5>To: ${email.recipients.join(', ')}</h5>
        <h5>Subject: ${email.subject}</h5>
        <hr>
        <p>${email.body}</p>
      `;

      // Mark the email as read
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      });
  });

  return false;
}


function send_email(event) {

  // Unpack the form data
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  console.log('Sending email to:', recipients, "\nSubject:", subject, "\nBody:", body);

  // Send a POST request to /emails
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      // If there was an error, throw it to be caught below, nofifying user
      throw new Error(result.error);
    } else if (result.message) {
      // Print result and redirect to sent folder on success (201 status code)
      console.log(result);
      
      // Redirect to sent mailbox
      load_mailbox('sent');
    }
  })
  .catch(error => {
    // Show alert on error codes
    console.error('Error:', error);
    alert(`An error occurred while sending the email.\n${error.message}`);
  });

  // Stop form from submitting, handle inside fetch result
  return false;  
}