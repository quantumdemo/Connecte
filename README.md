# Connecte: Link-in-Bio + Analytics (Micro SaaS)

Connecte is a powerful, open-source Link-in-Bio solution designed for creators. It allows you to build a personalized and easily-customizable page that houses all the important links you want to share with your audience. It's a perfect tool for social media bios, allowing you to drive traffic to your other content, products, and platforms.

This application is built with Flask and includes features like user accounts, link management, click tracking analytics, and premium subscription features powered by Paystack.

## Features

### Phase 1: Core Functionality
- **User Accounts:** Secure user registration and login system.
- **Profile Settings:** Users can set a profile username, bio, and a "Support Me" payment link.
- **Link Management:** A simple dashboard for users to add, edit, and manage multiple links.
- **Public Profile Page:** A clean, mobile-friendly public page at `linkme.com/@username` to display all links.
- **Basic Analytics:** Tracks the total number of clicks for each link.

### Phase 2: Premium Features
- **Subscription Tiers:** The application supports `free` and `premium` user accounts.
- **Paystack Integration:** A complete subscription workflow powered by Paystack to allow users to upgrade to the premium plan.
- **Premium Themes:** Premium users can choose from exclusive themes (e.g., Dark Mode) to customize their public profile page.
- **Link Limitations:** Free users are limited to 2 links, while premium users can add unlimited links.
- **Advanced Analytics:** Premium users get access to more detailed click analytics, including the visitor's IP address, user agent, and referrer.

## Tech Stack
- **Backend:** Python, Flask
- **Database:** SQLAlchemy (defaults to SQLite, configurable for PostgreSQL)
- **Database Migrations:** Flask-Migrate (using Alembic)
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF
- **Payments:** Paystack
- **Testing:** pytest, pytest-mock, pytest-cov
- **WSGI Server (for deployment):** Gunicorn

## Local Setup and Installation

Follow these steps to get the LinkMe application running on your local machine.

### 1. Prerequisites
- Python 3.8+
- `pip` for package installation
- `git` for cloning the repository

### 2. Clone the Repository
```bash
git clone <repository-url>
cd Connecte
```

### 3. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage the project's dependencies.
```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
Install all the required Python packages using the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the root of the project. You can use the provided `.env.example` as a template.
```bash
cp .env.example .env
```
Now, open the `.env` file and add your own values for the following variables:
- `SECRET_KEY`: A long, random string used to secure your application's sessions. You can generate one easily with `python -c 'import secrets; print(secrets.token_hex())'`.
- `DATABASE_URL` (Optional): If you want to use a database other than the default SQLite, provide the connection string here (e.g., for PostgreSQL).
- `PAYSTACK_SECRET_KEY`: Your secret API key from your Paystack dashboard.
- `PAYSTACK_PUBLIC_KEY`: Your public API key from your Paystack dashboard.

### 6. Run Database Migrations
Apply all the database migrations to set up your database schema.
```bash
export FLASK_APP=run.py  # On Windows, use `set FLASK_APP=run.py`
flask db upgrade
```

### 7. Run the Application
You can now run the Flask development server.
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

## Running Tests

To run the test suite and check for code coverage, use the following command:
```bash
export PYTHONPATH=.
pytest --cov=app --cov-report=term-missing
```

## Deployment

To deploy the Connecte application to a production environment, follow these general steps:

1.  **Choose a Hosting Provider:** Platforms like Heroku, DigitalOcean, AWS, or PythonAnywhere are good choices.
2.  **Use a Production WSGI Server:** The Flask development server is not suitable for production. Use a robust WSGI server like Gunicorn (which is included in `requirements.txt`).
    Example command to run the app with Gunicorn:
    ```bash
    gunicorn --bind 0.0.0.0:8000 run:app
    ```
3.  **Set Up a Production Database:** While SQLite is great for development, you should use a more robust database like PostgreSQL or MySQL for production. Make sure to set the `DATABASE_URL` environment variable on your hosting provider to point to your production database.
4.  **Configure Environment Variables:** Do not hardcode your secret keys or other sensitive information in the code. Set the `SECRET_KEY`, `DATABASE_URL`, `PAYSTACK_SECRET_KEY`, and `PAYSTACK_PUBLIC_KEY` as environment variables on your deployment server.
5.  **Serve Static Files:** For better performance, configure a web server like Nginx to serve your static files directly.

## Paystack Configuration

To enable the subscription features, you need to configure your Paystack account:

1.  **Create a Paystack Account:** If you don't have one, sign up at [paystack.com](https://paystack.com/).
2.  **Create a Subscription Plan:**
    - Go to the "Plans" section of your Paystack dashboard.
    - Create a new plan (e.g., ₦1,000/month).
    - Copy the **Plan Code** (it will look like `PLN_xxxxxxxxxxxxxxx`).
    - Open `app/main/routes.py` and replace the placeholder `plan_code` in the `subscribe()` function with your actual Plan Code.
3.  **Configure Webhooks:**
    - Go to the "Settings" > "API Keys & Webhooks" section of your Paystack dashboard.
    - In the "Webhook URL" field, enter the URL where your application will be hosted, followed by `/paystack-webhook`. For example: `https://your-domain.com/paystack-webhook`.
    - This allows Paystack to send events to your application to notify you of successful payments.

## Site Management

### Creating an Admin User

To create a user with admin privileges, you must first create a regular user account through the sign-up page. Then, from the command line on your server, run the following command:

```bash
export FLASK_APP=run.py
flask users grant-admin the_user's_email
```
This will grant admin privileges to the specified user, allowing them to access the `/admin` dashboard.

## Automated Subscription Management

This application includes a command to automatically downgrade users whose premium subscriptions have expired past their 7-day grace period.

To run this command manually:
```bash
export FLASK_APP=run.py
flask subscriptions:downgrade
```

For a production environment, it is highly recommended to automate this command to run once per day. You can do this using a cron job.

Example cron job to run the command every day at midnight:
```cron
0 0 * * * /path/to/your/project/venv/bin/flask subscriptions:downgrade >> /path/to/your/project/logs/cron.log 2>&1
```
Make sure to replace the paths with the actual paths to your project's virtual environment and log file.
