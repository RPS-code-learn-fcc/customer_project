# Company X's Customer Data Management App

- **Uses django-allauth to login in authorized users.

- **Permits CRUD operations on customer data**, including, but not limited to:
  - Addresses
  - Contact preferences
  - Event/program interests
  - Document storage for customer records, such as:
    - Program applications
    - Soil test results

- **Search customer data**, including:
  - Contact Information: Addresses, Phone Numbers, Emails
  - Documents
  - Notes

- **Mailing List Creation** by:
  1. Selecting interests and automatically adding customers
  2. Manually adding customers by customer name or customer mailing address

- **Activity tracking** for:
  - Customer creation
  - Note creation or editing (keeps track of note edits)
  - Document uploads (keeps track of document edits)

- **Can create and view a summarized customer profile**

- **Can filter home feed of customer information** based on:
  - Customer interests
  - Date customer was added
  - User who created/added the customer


## < Installation >

### Project Set Up
1. Create workspace: Create new folder on your personal device and open with preferred IDE (Visual Studio Code, etc.)
2. GitHub Desktop: Sign in with your Github username/email and pssword
3. Clone GitHub repository: Use GitHub Desktop to clone the repository 
4. Prepare static files: Copy the existing staticfiles folder and then rename it to "static" in the new project
5. Configure environment variables: Create the .env file and save it to the customer_project folder 

### Command Line
1. Install Python 
2. Activate Virtual Environment (eg. venv)
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver
  
  
---

## Django Management Commands

To seed (fake - using Faker) data into the app, run the following django management commands:

1. python manage.py app_users_seed_data
2. python manage.py customer_contact_methods_seed_data
3. python manage.py customer_interests_seed_data    
4. python manage.py customers_seed_data
  
## < Tailwind CSS Installation using Node >

Only make this installation if you are going to make changes to the styling of the site (Tailwind CSS)

### Tailwind Installation

1. Download node (if installed: node --version)
2. mkdir node && cd node
3. npm init -y && npm install tailwindcss @tailwindcss/cli && npm install cssnano 
4. Modify files:
#### # import tailwind into main css file: src/input.css
```
    @import "tailwindcss";
```
#### # package.json : scripts to run tailwind and use cssnano to minify stylesheet
```
  "scripts": {
    "minify": "npx cssnano /static/css/tailwind.css /static/css/tailwind.min.css"
  },
```

### Tailwind Build Process Commands 

#### Development
1. npm run tailwind
2. ctrl+c
npx @tailwindcss/cli -i ./src/input.css -o ./src/output.css --watch

#### Deployment
1. **Minify CSS**:
   Run this command to minify the CSS file:
   npx @tailwindcss/cli -i ./src/input.css -o ./static/output.css --watch
2. cd .. && python manage.py collectstatic