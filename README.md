!-- PROJECT LOGO -->
<br />
<p align="center">
	<img src="images/logo.png" alt="Logo" width="80" height="80">

	<h3 align="center">Online Docs Manager</h3>

	<p align="center">
		Application to store IDs of guests on Google Cloud and share it with you over GDrive
		<br />
		<a href="https://github.com/DivAgicha/Online-Docs-Manager-for-Hotels"><strong>Explore the docs »</strong></a>
		<br />
		<br />		·
		<a href="mailto:div.agicha@gmail.com">Report Bug</a>
		·
		<a href="mailto:div.agicha@gmail.com">Request Feature</a>
	</p>
</p>


## About The Project

As it's a usual process and task to take ID proof of all the guests arriving at the hotel to stay, instead of making copies of the ID, which consumes so much paper and difficult to maintain record of, we can upload a pic of that ID directly to google cloud with the ease to access it hierarchically in date-wise format with your own GDrive account.

### Prerequisites

This project requires Python (3.6 or higher) to be installed on the user system.

### Installation (for Windows & Linux)

1. Register for a account with [https://cloud.google.com/](Google Cloud Platform) at and head to [https://console.cloud.google.com/](Console) page.
2. Next you will need a Google Cloud Platform (GCP) project to hold your credentials, as this project uses OAuth 2.0 for authorization. Follow the steps at https://developers.google.com/assistant/sdk/guides/configure-developer-project to generate a file "client_secret_<client-id>.json".
3. Rename the file to "client_secret.json" and move it to Extras folder.
4. Clone the repo
	```sh
	git clone https://github.com/DivAgicha/Online-Docs-Manager-for-Hotels.git
	```
5. Change the directory to "Online-Docs-Manager-for-Hotels"
6. Open command prompt / shell to install 'venv' python package, used for creating a virtual environment
	```sh
	pip install virtualenv
	```
7. Create a virtual environment
	```sh
	virtualenv venv-py3
	```
8. Activate virtual environment
	```sh
	venv-py3/Scripts/activate
	```
9. Install all the required packages
	```sh
	pip install -r requirements.txt
	```
10. Open 'config.ini' in Extras folder and fill in the desired parameters value (MOST IMPORTANT)
11. Done! Now simply run the desired application, 'Scan n Upload.exe' to first scan the ID (using connected scanner) and then upload it cloud or 'Online Docs Manager.exe' to perform other operation like reading and saving previously uploaded IDs.



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- CONTACT -->
## Contact

Your Name - Divyansh Agicha - div.agicha@gmail.com

Project Link: [https://github.com/DivAgicha/Online-Docs-Manager-for-Hotels](https://github.com/DivAgicha/Online-Docs-Manager-for-Hotels)