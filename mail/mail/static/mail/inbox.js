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
        // Create a card to hold each email summary
        const email_card = document.createElement('div');
        email_card.className = 'card';
        email_card.style.cursor = 'pointer';
        email_card.style.marginBottom = '10px';

        if (email.read) {
          email_card.classList.add('bg-secondary');
          email_card.classList.add('text-white');
        }

        // Build the title field, dependent on mailbox type
        let title_field = '';
        if (mailbox === 'sent') {
          title_field = 'TO: ' + email.recipients.join(', ');
        } else {
          title_field = 'FROM: ' + email.sender;
        }
          
        // Add email details to the div
        email_card.innerHTML = `
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <strong>${title_field}</strong>
              <span>${email.timestamp}</span>
            </div>
            <div>${email.subject}</div>
          </div>
        `;

        // Add an event listener to read the email when clicked
        email_card.addEventListener('click', () => read_email(email.id));

        // Append the email card to the emails-view
        document.querySelector('#emails-view').appendChild(email_card);
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

      // Create a card to hold the email content
      const email_card = document.createElement('div');
      email_card.className = 'card bg-light';

      // Show the email content
      email_card.innerHTML = `
        <div class="card-header">
          <div class="d-flex justify-content-between">
            <h5>
              <span style="display: inline-block; width: 96px;">From:</span> 
              <strong>${email.sender}</strong>
            </h5>
            <span class="text-muted">on ${email.timestamp}</span>
          </div>
          <h5>
            <span style="display: inline-block; width: 96px;">To:</span> 
            <strong>${email.recipients.join(', ')}</strong>
          </h5>
          <h5>
            <span style="display: inline-block; width: 96px;">Subject:</span> 
            <strong>${email.subject}</strong>
          </h5>
        </div>
        <div class="card-body">
          ${email.body.replace(/\n/g, '<br>')}
        </div>
      `;

      // Eliminate the placeholder text
      document.querySelector('#emails-view').innerHTML = '';

      // Append the email card to the emails-view
      document.querySelector('#emails-view').appendChild(email_card);

      // Mark the email as read
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      });

      // Create a container for the archive and reply buttons on the bottom
      const button_container = document.createElement('div');
      button_container.className = 'button-group mt-3';

      // Add an archive/unarchive button
      const archive_button = document.createElement('button');
      archive_button.className = 'btn btn-sm btn-outline-danger';
      archive_button.innerText = email.archived ? 'Unarchive' : 'Archive';
      archive_button.addEventListener('click', () => {
        // Toggle the archived status
        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
              archived: !email.archived
          })
        })
        .then(() => {
          // After archiving/unarchiving, load the inbox
          load_mailbox('inbox');
        });
      })
      button_container.appendChild(archive_button);

      // Add a reply button
      const reply_button = document.createElement('button');
      reply_button.className = 'btn btn-sm btn-outline-primary ml-2';
      reply_button.innerText = 'Reply';
      reply_button.addEventListener('click', () => {
        // Compose a reply
        compose_email();

        // Pre-fill the compose fields
        document.querySelector('#compose-recipients').value = email.sender;
        let subject_prefix = email.subject.startsWith('Re:') ? '' : 'Re: ';
        document.querySelector('#compose-subject').value = subject_prefix + email.subject;
        document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp}, ${email.sender} wrote:\n${email.body}`;
      });
      button_container.appendChild(reply_button);

      document.querySelector('#emails-view').appendChild(button_container);
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