# Udacity Course Video Downloader

A Python-based automation tool designed to help Udacity students download course videos for offline viewing. This tool uses Selenium WebDriver to navigate through Udacity's platform and download course content.

## Features

- Automated login to Udacity platform
- Course search and navigation
- Video collection and downloading
- Video concatenation capability
- Enhanced browser automation with stealth features
- Cross-platform compatibility

## Prerequisites

Before running this project, make sure you have the following installed:
- Python 3.7+
- Chrome browser
- Required Python packages (see Installation section)

## Installation

1. Clone the repository: https://github.com/andykofman/UdaGrab
2. cd UdaGrab


The script will:
- Log into your Udacity account
- Navigate to the specified course
- Collect video URLs
- Download videos to the `downloaded_videos` directory
- Optionally concatenate all videos into a single file

## Project Structure

UdaGrab/
│
├── UdacityGrab.py        # Main script file
└── downloaded_videos/   # Directory for downloaded content
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore file
├── README.md            # This file
└── downloaded_videos/   # Directory for downloaded content

## Error Handling

The script includes error handling for common issues:
- Login failures
- Navigation errors
- Download problems
- Network connectivity issues

Screenshots are saved automatically if errors occur during execution.
  
## Important Notes

- This tool is for personal use only
- Respect Udacity's terms of service and content policies
- Downloaded content should only be used for personal offline viewing
- Be mindful of your storage space when downloading videos


  ## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring their use of this tool complies with Udacity's terms of service and relevant laws and regulations.


## Contact

For questions or feedback, please contact [ali.a@aucegypt.edu](mailto:ali.a@aucegypt.edu).
